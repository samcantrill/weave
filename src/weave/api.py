"""Public config composition API."""

from __future__ import annotations

from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, cast

from ._argv import (
    ArgvScopedOverlay,
    ArgvUnparsedArg,
    ArgvValueOverride,
    ParsedConfigArgs,
    ParsedConfigArgv,
    ScopedOverlayCandidate,
    ScopedOverlayCandidateOrigin,
    parse_config_args as _parse_config_args,
)
from .digests import Fingerprint
from .plain import PlainData, ensure_plain_data, to_plain_data
from .errors import ConfigError, ConfigErrorContext, ConfigValidationError, PlainDataError

from .artifacts import (
    SCHEMA_VERSION as ARTIFACT_SCHEMA_VERSION,
    CompositionManifest,
    ConfigFingerprintRecord,
    RawSourceSnapshotBundle,
    RawSourceSnapshotPayload,
    RawSourceSnapshotReference,
    SourceArtifactRecord,
)
from .fingerprints import (
    ARTIFACT_SAFE_FINGERPRINT_LABEL,
    ARTIFACT_SAFE_FINGERPRINT_POLICY,
    ARTIFACT_SAFE_RUNTIME_REPLAY,
    ConfigFingerprintComparison,
    compare_config_artifact_fingerprints,
)
from .provenance import ConfigProvenance
from .recipes import RecipeCatalog, RecipeImplementation
from .structural import (
    StructuralResolutionRecord,
    StructuralResolutionRequest,
    StructuralResolutionResult,
    StructuralResolverDefinition,
    StructuralResolverRejected,
    _ensure_no_unresolved_structural_directives,
    resolve_structural,
)


__default_recipe_catalog: RecipeCatalog | None = None


@dataclass(frozen=True, slots=True)
class ConfigCompositionStageRecord:
    name: str
    status: Literal["completed", "skipped", "failed"]
    payload: dict[str, PlainData]

    def __post_init__(self) -> None:
        if self.name == "":
            raise ConfigValidationError("ConfigCompositionStageRecord.name must be non-empty")
        if self.status not in {"completed", "skipped", "failed"}:
            raise ConfigValidationError(f"Unsupported stage status: {self.status!r}")

        try:
            payload = to_plain_data(self.payload, path=f"ConfigCompositionStageRecord[{self.name}].payload")
        except Exception as exc:  # noqa: BLE001
            raise ConfigValidationError("stage payload must be plain data") from exc

        if not isinstance(payload, dict):
            raise ConfigValidationError("ConfigCompositionStageRecord.payload must be a mapping")
        object.__setattr__(self, "payload", cast(dict[str, PlainData], payload))


@dataclass(frozen=True, slots=True)
class ConfigCompositionInspection:
    stages: tuple[ConfigCompositionStageRecord, ...]
    unresolved: dict[str, PlainData]
    resolved: dict[str, PlainData]
    redacted: dict[str, PlainData]
    provenance: ConfigProvenance
    recipe_manifest: tuple[dict[str, PlainData], ...]
    fingerprint: Fingerprint
    manifest: CompositionManifest
    source_artifacts: tuple[SourceArtifactRecord, ...]
    fingerprint_records: tuple[ConfigFingerprintRecord, ...]
    raw_source_snapshots: RawSourceSnapshotBundle

    def __post_init__(self) -> None:
        if not isinstance(self.stages, tuple):
            raise ConfigValidationError("ConfigCompositionInspection.stages must be a tuple")

        plain_unresolved = ensure_plain_data(self.unresolved, path="ConfigCompositionInspection.unresolved")
        plain_resolved = ensure_plain_data(self.resolved, path="ConfigCompositionInspection.resolved")
        plain_redacted = ensure_plain_data(self.redacted, path="ConfigCompositionInspection.redacted")

        if not isinstance(plain_unresolved, dict):
            raise ConfigValidationError("ConfigCompositionInspection.unresolved must be a mapping")
        if not isinstance(plain_resolved, dict):
            raise ConfigValidationError("ConfigCompositionInspection.resolved must be a mapping")
        if not isinstance(plain_redacted, dict):
            raise ConfigValidationError("ConfigCompositionInspection.redacted must be a mapping")

        normalized_manifest = tuple(self.recipe_manifest)
        if not isinstance(normalized_manifest, tuple):
            raise ConfigValidationError("ConfigCompositionInspection.recipe_manifest must be a tuple")

        for index, item in enumerate(normalized_manifest):
            if not isinstance(item, dict):
                raise ConfigValidationError(f"recipe_manifest[{index}] must be a mapping")
            ensure_plain_data(item, path=f"ConfigCompositionInspection.recipe_manifest[{index}]")

        if not isinstance(self.source_artifacts, tuple):
            raise ConfigValidationError("ConfigCompositionInspection.source_artifacts must be a tuple")
        if not isinstance(self.fingerprint_records, tuple):
            raise ConfigValidationError("ConfigCompositionInspection.fingerprint_records must be a tuple")
        if not isinstance(self.raw_source_snapshots, RawSourceSnapshotBundle):
            raise ConfigValidationError(
                "ConfigCompositionInspection.raw_source_snapshots must be a RawSourceSnapshotBundle"
            )

        for index, source_artifact in enumerate(self.source_artifacts):
            if not isinstance(source_artifact, SourceArtifactRecord):
                raise ConfigValidationError(
                    f"source_artifacts[{index}] must be SourceArtifactRecord"
                )

        for index, fingerprint_record in enumerate(self.fingerprint_records):
            if not isinstance(fingerprint_record, ConfigFingerprintRecord):
                raise ConfigValidationError(
                    f"fingerprint_records[{index}] must be ConfigFingerprintRecord"
                )

        object.__setattr__(self, "unresolved", cast(dict[str, PlainData], plain_unresolved))
        object.__setattr__(self, "resolved", cast(dict[str, PlainData], plain_resolved))
        object.__setattr__(self, "redacted", cast(dict[str, PlainData], plain_redacted))
        object.__setattr__(self, "recipe_manifest", normalized_manifest)

    def stage(self, name: str) -> ConfigCompositionStageRecord | None:
        for item in self.stages:
            if item.name == name:
                return item
        return None

    def to_composed_config(self) -> "ComposedConfig":
        return ComposedConfig(
            resolved=self.resolved,
            redacted=self.redacted,
            provenance=self.provenance,
            recipe_manifest=self.recipe_manifest,
            fingerprint=self.fingerprint,
            unresolved=self.unresolved,
            manifest=self.manifest,
            source_artifacts=self.source_artifacts,
            fingerprint_records=self.fingerprint_records,
            raw_source_snapshots=self.raw_source_snapshots,
        )


@dataclass(frozen=True, slots=True)
class ComposedConfig:
    resolved: dict[str, PlainData]
    redacted: dict[str, PlainData]
    provenance: ConfigProvenance
    recipe_manifest: tuple[dict[str, PlainData], ...]
    fingerprint: Fingerprint
    unresolved: dict[str, PlainData] = field(default_factory=dict)
    manifest: CompositionManifest = field(
        default_factory=lambda: CompositionManifest(
            schema_version=ARTIFACT_SCHEMA_VERSION,
            source_artifacts=(),
            fingerprint_records=(),
            recipe_manifest=(),
            metadata={},
        )
    )
    source_artifacts: tuple[SourceArtifactRecord, ...] = ()
    fingerprint_records: tuple[ConfigFingerprintRecord, ...] = ()
    raw_source_snapshots: RawSourceSnapshotBundle = field(
        default_factory=lambda: RawSourceSnapshotBundle(
            schema_version=ARTIFACT_SCHEMA_VERSION,
            enabled=False,
            payloads=(),
            references=(),
            metadata={"reason": "not_requested_default"},
        )
    )


@dataclass(frozen=True, slots=True)
class ConfigArgvWarning:
    code: str
    message: str
    source_order: int
    token: str
    path: str | None
    remediation: str | None
    details: dict[str, PlainData] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.code:
            raise ConfigValidationError("ConfigArgvWarning.code must be non-empty")
        if not self.message:
            raise ConfigValidationError("ConfigArgvWarning.message must be non-empty")
        if self.source_order < -1:
            raise ConfigValidationError("ConfigArgvWarning.source_order must be >= -1")
        if not isinstance(self.token, str):
            raise ConfigValidationError("ConfigArgvWarning.token must be a string")
        if self.path is not None and not isinstance(self.path, str):
            raise ConfigValidationError("ConfigArgvWarning.path must be a string or None")
        if self.remediation is not None and not isinstance(self.remediation, str):
            raise ConfigValidationError("ConfigArgvWarning.remediation must be a string or None")

        try:
            details = ensure_plain_data(self.details, path=f"ConfigArgvWarning[{self.code}].details")
        except Exception as exc:  # noqa: BLE001
            raise ConfigValidationError("ConfigArgvWarning.details must be plain data") from exc
        if not isinstance(details, dict):
            raise ConfigValidationError("ConfigArgvWarning.details must be a mapping")
        object.__setattr__(self, "details", cast(dict[str, PlainData], details))

    def to_dict(self) -> dict[str, PlainData]:
        return {
            "code": self.code,
            "message": self.message,
            "source_order": self.source_order,
            "token": self.token,
            "path": self.path,
            "remediation": self.remediation,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class ConfigArgvCompositionResult:
    command: str
    base_config_path: str
    parsed_argv: ParsedConfigArgv
    value_overrides: tuple[ArgvValueOverride, ...]
    scoped_overlays: tuple[ArgvScopedOverlay, ...]
    unparsed_args: tuple[ArgvUnparsedArg, ...]
    warnings: tuple[ConfigArgvWarning, ...]
    composed_config: ComposedConfig

    def __post_init__(self) -> None:
        _validate_argv_result_common(
            command=self.command,
            base_config_path=self.base_config_path,
            parsed_argv=self.parsed_argv,
            value_overrides=self.value_overrides,
            scoped_overlays=self.scoped_overlays,
            unparsed_args=self.unparsed_args,
            warnings=self.warnings,
        )
        if not isinstance(self.composed_config, ComposedConfig):
            raise ConfigValidationError("ConfigArgvCompositionResult.composed_config must be ComposedConfig")
        object.__setattr__(self, "value_overrides", tuple(self.value_overrides))
        object.__setattr__(self, "scoped_overlays", tuple(self.scoped_overlays))
        object.__setattr__(self, "unparsed_args", tuple(self.unparsed_args))
        object.__setattr__(self, "warnings", tuple(self.warnings))

    def to_dict(self) -> dict[str, PlainData]:
        return {
            **_argv_result_metadata_to_dict(
                command=self.command,
                base_config_path=self.base_config_path,
                parsed_argv=self.parsed_argv,
                value_overrides=self.value_overrides,
                scoped_overlays=self.scoped_overlays,
                unparsed_args=self.unparsed_args,
                warnings=self.warnings,
            ),
            "composed_config": _composed_config_to_dict(self.composed_config),
        }


@dataclass(frozen=True, slots=True)
class ConfigArgvInspectionResult:
    command: str
    base_config_path: str
    parsed_argv: ParsedConfigArgv
    value_overrides: tuple[ArgvValueOverride, ...]
    scoped_overlays: tuple[ArgvScopedOverlay, ...]
    unparsed_args: tuple[ArgvUnparsedArg, ...]
    warnings: tuple[ConfigArgvWarning, ...]
    inspection: ConfigCompositionInspection

    def __post_init__(self) -> None:
        _validate_argv_result_common(
            command=self.command,
            base_config_path=self.base_config_path,
            parsed_argv=self.parsed_argv,
            value_overrides=self.value_overrides,
            scoped_overlays=self.scoped_overlays,
            unparsed_args=self.unparsed_args,
            warnings=self.warnings,
        )
        if not isinstance(self.inspection, ConfigCompositionInspection):
            raise ConfigValidationError("ConfigArgvInspectionResult.inspection must be ConfigCompositionInspection")
        object.__setattr__(self, "value_overrides", tuple(self.value_overrides))
        object.__setattr__(self, "scoped_overlays", tuple(self.scoped_overlays))
        object.__setattr__(self, "unparsed_args", tuple(self.unparsed_args))
        object.__setattr__(self, "warnings", tuple(self.warnings))

    def to_composed_config(self) -> ComposedConfig:
        return self.inspection.to_composed_config()

    def to_dict(self) -> dict[str, PlainData]:
        return {
            **_argv_result_metadata_to_dict(
                command=self.command,
                base_config_path=self.base_config_path,
                parsed_argv=self.parsed_argv,
                value_overrides=self.value_overrides,
                scoped_overlays=self.scoped_overlays,
                unparsed_args=self.unparsed_args,
                warnings=self.warnings,
            ),
            "inspection": _inspection_to_dict(self.inspection),
        }


@dataclass(frozen=True, slots=True)
class ConfigBaseRequest:
    base_context: object | None = None


@dataclass(frozen=True, slots=True)
class ConfigBaseResolution:
    base_config_path: str | Path
    details: Mapping[str, PlainData] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.base_config_path, (str, Path)):
            raise ConfigValidationError("ConfigBaseResolution.base_config_path must be a path string or Path")
        base_config_path = str(self.base_config_path)
        if base_config_path == "":
            raise ConfigValidationError("ConfigBaseResolution.base_config_path must be non-empty")

        details: dict[str, PlainData] | None
        if self.details is None:
            details = None
        else:
            try:
                plain_details = ensure_plain_data(self.details, path="ConfigBaseResolution.details")
            except PlainDataError as exc:
                raise ConfigValidationError("ConfigBaseResolution.details must be plain data") from exc
            if not isinstance(plain_details, dict):
                raise ConfigValidationError("ConfigBaseResolution.details must be a mapping")
            details = cast(dict[str, PlainData], plain_details)

        object.__setattr__(self, "base_config_path", base_config_path)
        object.__setattr__(self, "details", details)

    def to_dict(self) -> dict[str, PlainData]:
        payload: dict[str, PlainData] = {"base_config_path": str(self.base_config_path)}
        if self.details is not None:
            payload["details"] = cast(dict[str, PlainData], self.details)
        return payload


@dataclass(frozen=True, slots=True)
class ConfigArgsCompositionResult:
    base_config_path: str
    parsed_args: ParsedConfigArgs
    value_overrides: tuple[ArgvValueOverride, ...]
    scoped_overlays: tuple[ArgvScopedOverlay, ...]
    unparsed_args: tuple[ArgvUnparsedArg, ...]
    warnings: tuple[ConfigArgvWarning, ...]
    composed_config: ComposedConfig
    base_details: tuple[dict[str, PlainData], ...] = ()
    objects: Mapping[str, object] = field(default_factory=dict)
    selected_objects: tuple[dict[str, PlainData], ...] = ()

    def __post_init__(self) -> None:
        _validate_config_args_result_common(
            base_config_path=self.base_config_path,
            parsed_args=self.parsed_args,
            value_overrides=self.value_overrides,
            scoped_overlays=self.scoped_overlays,
            unparsed_args=self.unparsed_args,
            warnings=self.warnings,
        )
        if not isinstance(self.composed_config, ComposedConfig):
            raise ConfigValidationError("ConfigArgsCompositionResult.composed_config must be ComposedConfig")
        object.__setattr__(self, "value_overrides", tuple(self.value_overrides))
        object.__setattr__(self, "scoped_overlays", tuple(self.scoped_overlays))
        object.__setattr__(self, "unparsed_args", tuple(self.unparsed_args))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        object.__setattr__(self, "base_details", _normalize_base_details(self.base_details))
        if not isinstance(self.objects, Mapping):
            raise ConfigValidationError("ConfigArgsCompositionResult.objects must be a mapping")
        objects = dict(self.objects)
        for key in objects:
            if not isinstance(key, str) or key == "":
                raise ConfigValidationError("ConfigArgsCompositionResult.objects keys must be non-empty strings")
        object.__setattr__(self, "objects", objects)
        object.__setattr__(self, "selected_objects", _normalize_selected_object_metadata(self.selected_objects))

    def to_dict(self) -> dict[str, PlainData]:
        return {
            **_config_args_result_metadata_to_dict(
                base_config_path=self.base_config_path,
                parsed_args=self.parsed_args,
                value_overrides=self.value_overrides,
                scoped_overlays=self.scoped_overlays,
                unparsed_args=self.unparsed_args,
                warnings=self.warnings,
                base_details=self.base_details,
                selected_objects=self.selected_objects,
            ),
            "composed_config": _composed_config_to_dict(self.composed_config),
        }


@dataclass(frozen=True, slots=True)
class ConfigArgsInspectionResult:
    base_config_path: str
    parsed_args: ParsedConfigArgs
    value_overrides: tuple[ArgvValueOverride, ...]
    scoped_overlays: tuple[ArgvScopedOverlay, ...]
    unparsed_args: tuple[ArgvUnparsedArg, ...]
    warnings: tuple[ConfigArgvWarning, ...]
    inspection: ConfigCompositionInspection
    base_details: tuple[dict[str, PlainData], ...] = ()

    def __post_init__(self) -> None:
        _validate_config_args_result_common(
            base_config_path=self.base_config_path,
            parsed_args=self.parsed_args,
            value_overrides=self.value_overrides,
            scoped_overlays=self.scoped_overlays,
            unparsed_args=self.unparsed_args,
            warnings=self.warnings,
        )
        if not isinstance(self.inspection, ConfigCompositionInspection):
            raise ConfigValidationError("ConfigArgsInspectionResult.inspection must be ConfigCompositionInspection")
        object.__setattr__(self, "value_overrides", tuple(self.value_overrides))
        object.__setattr__(self, "scoped_overlays", tuple(self.scoped_overlays))
        object.__setattr__(self, "unparsed_args", tuple(self.unparsed_args))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        object.__setattr__(self, "base_details", _normalize_base_details(self.base_details))

    def to_composed_config(self) -> ComposedConfig:
        return self.inspection.to_composed_config()

    def to_dict(self) -> dict[str, PlainData]:
        return {
            **_config_args_result_metadata_to_dict(
                base_config_path=self.base_config_path,
                parsed_args=self.parsed_args,
                value_overrides=self.value_overrides,
                scoped_overlays=self.scoped_overlays,
                unparsed_args=self.unparsed_args,
                warnings=self.warnings,
                base_details=self.base_details,
            ),
            "inspection": _inspection_to_dict(self.inspection),
        }



@dataclass(frozen=True, slots=True)
class ConfigEntrypoint:
    base_config_path: str | Path | None = None
    base_resolver: Callable[[ConfigBaseRequest], ConfigBaseResolution] | None = None
    base_context: object | None = None
    recipe_catalog: RecipeCatalog | None = None
    allow_unparsed: bool = False
    include_raw_source_snapshots: bool = False
    selected_objects: Sequence[str] | Mapping[str, str] = ()
    runtime: Mapping[str, object] | None = None
    _selected_object_specs: tuple[dict[str, PlainData], ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.recipe_catalog is not None and not isinstance(self.recipe_catalog, RecipeCatalog):
            raise ConfigValidationError("recipe_catalog must be a RecipeCatalog")
        if not isinstance(self.allow_unparsed, bool):
            raise ConfigValidationError("allow_unparsed must be a bool")
        if not isinstance(self.include_raw_source_snapshots, bool):
            raise ConfigValidationError("include_raw_source_snapshots must be a bool")
        selected_object_specs = _normalize_selected_object_specs(self.selected_objects)
        object.__setattr__(self, "_selected_object_specs", selected_object_specs)
        if self.runtime is not None and not isinstance(self.runtime, Mapping):
            raise _selected_instantiation_error(
                "runtime must be a mapping when provided",
                code="invalid_selected_runtime",
                expected="mapping",
                actual=type(self.runtime).__name__,
                details={"actual_type": type(self.runtime).__name__},
            )

        base_config_path = self.base_config_path
        has_fixed_base = base_config_path is not None
        has_resolver = self.base_resolver is not None
        if has_fixed_base == has_resolver:
            code = "conflicting_base_strategies" if has_fixed_base else "missing_base_strategy"
            raise _base_resolution_error(
                "ConfigEntrypoint requires exactly one base strategy",
                code=code,
                details={
                    "has_base_config_path": has_fixed_base,
                    "has_base_resolver": has_resolver,
                },
            )

        if base_config_path is not None:
            parsed = _parse_config_args(
                (),
                base_config_path=base_config_path,
                allow_unparsed=self.allow_unparsed,
            )
            object.__setattr__(self, "base_config_path", parsed.base_config_path)
            return

        if not callable(self.base_resolver):
            raise _base_resolution_error(
                "base_resolver must be callable",
                code="invalid_base_resolver",
                details={"actual_type": type(self.base_resolver).__name__},
            )

    def compose_args(self, config_args: Sequence[str] = ()) -> ConfigArgsCompositionResult:
        inspection_result = self.inspect_args(config_args)
        composed_config = inspection_result.inspection.to_composed_config()
        selected_objects = self._selected_object_specs
        objects = _instantiate_selected_objects(
            composed_config.resolved,
            selected_objects=selected_objects,
            runtime=self.runtime,
        )
        return ConfigArgsCompositionResult(
            base_config_path=inspection_result.base_config_path,
            parsed_args=inspection_result.parsed_args,
            value_overrides=inspection_result.value_overrides,
            scoped_overlays=inspection_result.scoped_overlays,
            unparsed_args=inspection_result.unparsed_args,
            warnings=inspection_result.warnings,
            composed_config=composed_config,
            base_details=inspection_result.base_details,
            objects=objects,
            selected_objects=selected_objects,
        )

    def inspect_args(self, config_args: Sequence[str] = ()) -> ConfigArgsInspectionResult:
        base_config_path, base_details = self._resolve_base()
        result = inspect_config_args(
            base_config_path,
            config_args=config_args,
            allow_unparsed=self.allow_unparsed,
            recipe_catalog=self.recipe_catalog,
            include_raw_source_snapshots=self.include_raw_source_snapshots,
        )
        return ConfigArgsInspectionResult(
            base_config_path=result.base_config_path,
            parsed_args=result.parsed_args,
            value_overrides=result.value_overrides,
            scoped_overlays=result.scoped_overlays,
            unparsed_args=result.unparsed_args,
            warnings=result.warnings,
            inspection=result.inspection,
            base_details=base_details,
        )

    def _resolve_base(self) -> tuple[str, tuple[dict[str, PlainData], ...]]:
        if self.base_resolver is None:
            if self.base_config_path is None:
                raise _base_resolution_error("Missing base strategy", code="missing_base_strategy")
            return str(self.base_config_path), ()

        resolved = self.base_resolver(ConfigBaseRequest(base_context=self.base_context))
        if not isinstance(resolved, ConfigBaseResolution):
            raise _base_resolution_error(
                "base_resolver must return ConfigBaseResolution",
                code="invalid_base_resolution",
                details={"actual_type": type(resolved).__name__},
            )
        base_details = (cast(dict[str, PlainData], resolved.details),) if resolved.details is not None else ()
        return str(resolved.base_config_path), base_details


def compose_config_from_args(
    base_config_path: str | Path,
    config_args: Sequence[str] = (),
    *,
    allow_unparsed: bool = False,
    recipe_catalog: RecipeCatalog | None = None,
    include_raw_source_snapshots: bool = False,
) -> ConfigArgsCompositionResult:
    inspection_result = inspect_config_args(
        base_config_path=base_config_path,
        config_args=config_args,
        allow_unparsed=allow_unparsed,
        recipe_catalog=recipe_catalog,
        include_raw_source_snapshots=include_raw_source_snapshots,
    )
    return ConfigArgsCompositionResult(
        base_config_path=inspection_result.base_config_path,
        parsed_args=inspection_result.parsed_args,
        value_overrides=inspection_result.value_overrides,
        scoped_overlays=inspection_result.scoped_overlays,
        unparsed_args=inspection_result.unparsed_args,
        warnings=inspection_result.warnings,
        composed_config=inspection_result.inspection.to_composed_config(),
        base_details=inspection_result.base_details,
    )


def inspect_config_args(
    base_config_path: str | Path,
    config_args: Sequence[str] = (),
    *,
    allow_unparsed: bool = False,
    recipe_catalog: RecipeCatalog | None = None,
    include_raw_source_snapshots: bool = False,
) -> ConfigArgsInspectionResult:
    from .compose import _inspect_config_composition_with_argv_scoped_overlays

    if recipe_catalog is not None and not isinstance(recipe_catalog, RecipeCatalog):
        raise ConfigValidationError("recipe_catalog must be a RecipeCatalog")
    if not isinstance(include_raw_source_snapshots, bool):
        raise ConfigValidationError("include_raw_source_snapshots must be a bool")

    catalog = recipe_catalog if recipe_catalog is not None else _get_default_recipe_catalog()
    parsed = _parse_config_args(
        config_args,
        base_config_path=base_config_path,
        allow_unparsed=allow_unparsed,
    )
    inspection = _inspect_config_composition_with_argv_scoped_overlays(
        parsed.base_config_path,
        recipe_catalog=catalog,
        argv_scoped_overlays=parsed.scoped_overlays,
        overrides=parsed.override_strings,
        include_raw_source_snapshots=include_raw_source_snapshots,
    )
    warnings = _argv_warnings(parsed=parsed, recipe_catalog=catalog)
    return ConfigArgsInspectionResult(
        base_config_path=parsed.base_config_path,
        parsed_args=parsed,
        value_overrides=parsed.value_overrides,
        scoped_overlays=parsed.scoped_overlays,
        unparsed_args=parsed.unparsed_args,
        warnings=warnings,
        inspection=inspection,
    )


def compose_config_from_argv(
    argv: Sequence[str] | None = None,
    *,
    command_choices: Collection[str] | None = None,
    allow_unparsed: bool = False,
    recipe_catalog: RecipeCatalog | None = None,
    include_raw_source_snapshots: bool = False,
) -> ConfigArgsCompositionResult:
    inspection_result = inspect_config_from_argv(
        argv=argv,
        command_choices=command_choices,
        allow_unparsed=allow_unparsed,
        recipe_catalog=recipe_catalog,
        include_raw_source_snapshots=include_raw_source_snapshots,
    )
    return ConfigArgsCompositionResult(
        base_config_path=inspection_result.base_config_path,
        parsed_args=inspection_result.parsed_args,
        value_overrides=inspection_result.value_overrides,
        scoped_overlays=inspection_result.scoped_overlays,
        unparsed_args=inspection_result.unparsed_args,
        warnings=inspection_result.warnings,
        composed_config=inspection_result.inspection.to_composed_config(),
        base_details=inspection_result.base_details,
    )


def inspect_config_from_argv(
    argv: Sequence[str] | None = None,
    *,
    command_choices: Collection[str] | None = None,
    allow_unparsed: bool = False,
    recipe_catalog: RecipeCatalog | None = None,
    include_raw_source_snapshots: bool = False,
) -> ConfigArgsInspectionResult:
    tokens = _normalize_retained_argv(argv)
    choices = _normalize_retained_command_choices(command_choices)
    if _looks_like_command_first_argv(tokens, command_choices=choices):
        raise _argv_helper_error(
            "compose_config_from_argv no longer accepts '<command> <base-config> ...' argv shapes",
            code="command_first_argv_migration",
            order=0,
            details={
                "legacy_shape": "<command> <base-config> ...",
                "first_token": tokens[0],
                "base_config_path_candidate": tokens[1],
            },
        )
    if choices is not None:
        raise _argv_helper_error(
            "command_choices are not supported by commandless argv helpers",
            code="unsupported_command_choices",
            order=-1,
            details={"command_choices": list(choices)},
        )
    if not tokens:
        raise _argv_helper_error(
            "Missing base config path token in argv",
            code="missing_base_config_path",
            order=0,
        )
    if tokens[0] == "":
        raise _argv_helper_error(
            "Base config path token must be non-empty",
            code="empty_base_config_path",
            order=0,
        )

    return inspect_config_args(
        base_config_path=tokens[0],
        config_args=tokens[1:],
        allow_unparsed=allow_unparsed,
        recipe_catalog=recipe_catalog,
        include_raw_source_snapshots=include_raw_source_snapshots,
    )


def _normalize_retained_argv(argv: Sequence[str] | None) -> tuple[str, ...]:
    if argv is None:
        raise _argv_helper_error(
            "argv must be provided explicitly; implicit sys.argv is not supported",
            code="missing_explicit_argv",
            order=-1,
        )
    if isinstance(argv, str):
        raise _argv_helper_error(
            "argv must be a sequence of strings, not one string",
            code="invalid_argv",
            order=-1,
            details={"actual_type": "str"},
        )

    try:
        tokens = tuple(argv)
    except TypeError as exc:
        raise _argv_helper_error(
            "argv must be a sequence of strings",
            code="invalid_argv",
            order=-1,
            details={"actual_type": type(argv).__name__},
        ) from exc

    for order, token in enumerate(tokens):
        if not isinstance(token, str):
            raise _argv_helper_error(
                f"argv token at order {order} must be text",
                code="invalid_argv_token_type",
                order=order,
                expected="str",
                actual=type(token).__name__,
                details={"actual_type": type(token).__name__},
            )
    return tokens


def _normalize_retained_command_choices(command_choices: Collection[str] | None) -> tuple[str, ...] | None:
    if command_choices is None:
        return None
    if isinstance(command_choices, str):
        raise _argv_helper_error(
            "command_choices are not supported by commandless argv helpers",
            code="unsupported_command_choices",
            order=-1,
            details={"actual_type": "str"},
        )

    choices = tuple(command_choices)
    for index, choice in enumerate(choices):
        if not isinstance(choice, str) or choice == "":
            raise _argv_helper_error(
                "command_choices entries must be non-empty strings",
                code="unsupported_command_choices",
                order=-1,
                details={"choice_index": index, "actual": repr(choice)},
            )
    return tuple(sorted(choices))


def _looks_like_command_first_argv(tokens: tuple[str, ...], *, command_choices: tuple[str, ...] | None) -> bool:
    if len(tokens) < 2:
        return False
    if command_choices is not None and tokens[0] in command_choices:
        return True
    if _looks_like_config_arg_token(tokens[0]):
        return False
    return _looks_like_base_config_path_token(tokens[1])


def _looks_like_config_arg_token(token: str) -> bool:
    return token.startswith("-") or "=" in token


def _looks_like_base_config_path_token(token: str) -> bool:
    return token.endswith((".yaml", ".yml")) or "/" in token or "\\" in token


def _argv_helper_error(
    message: str,
    *,
    code: str,
    order: int,
    expected: PlainData | None = None,
    actual: PlainData | None = None,
    details: dict[str, PlainData] | None = None,
) -> ConfigValidationError:
    return ConfigValidationError(
        message,
        context=ConfigErrorContext(
            code=code,
            source_kind="argv",
            source_order=order,
            source_path="<argv>",
            expected=expected,
            actual=actual,
            directive="config_args_shorthand",
            remediation=_argv_helper_remediation(code),
            details=details,
        ),
    )


def _argv_helper_remediation(code: str) -> str | None:
    if code == "command_first_argv_migration":
        return "Use compose_config_from_args(base_config_path, config_args=...) or pass '<base-config> ...' without a command token."
    if code == "missing_explicit_argv":
        return "Pass an explicit argv sequence; implicit sys.argv is not supported."
    if code in {"missing_base_config_path", "empty_base_config_path"}:
        return "Pass argv as '<base-config> [config-args...]' or use compose_config_from_args(...)."
    if code == "unsupported_command_choices":
        return "Parse project commands downstream and pass only remaining config args to Weave."
    if code == "invalid_argv":
        return "Pass argv as an explicit sequence of strings."
    if code == "invalid_argv_token_type":
        return "Pass only string values in argv."
    return None


def _base_resolution_error(
    message: str,
    *,
    code: str,
    details: dict[str, PlainData] | None = None,
) -> ConfigValidationError:
    return ConfigValidationError(
        message,
        context=ConfigErrorContext(
            code=code,
            source_kind="config_entrypoint",
            source_order=-1,
            source_path="<config-entrypoint>",
            directive="base_resolution",
            remediation=_base_resolution_remediation(code),
            details=details,
        ),
    )


def _base_resolution_remediation(code: str) -> str | None:
    if code == "missing_base_strategy":
        return "Pass either base_config_path or base_resolver to ConfigEntrypoint."
    if code == "conflicting_base_strategies":
        return "Pass exactly one base strategy: base_config_path or base_resolver."
    if code == "invalid_base_resolver":
        return "Pass a callable base_resolver or use base_config_path for fixed-base composition."
    if code == "invalid_base_resolution":
        return "Return ConfigBaseResolution(base_config_path=..., details=...) from base_resolver."
    return None


def _argv_warnings(*, parsed: ParsedConfigArgv | ParsedConfigArgs, recipe_catalog: RecipeCatalog) -> tuple[ConfigArgvWarning, ...]:
    candidates_by_override = {
        override: _warning_candidates(parsed.base_config_path, override)
        for override in parsed.value_overrides
        if override.operation == "update" and isinstance(override.value, str)
    }
    candidates_by_override = {
        override: candidates
        for override, candidates in candidates_by_override.items()
        if any(candidate.exists for candidate in candidates)
    }
    if not candidates_by_override:
        return ()

    try:
        from .compose import _inspect_config_composition_with_argv_scoped_overlays

        pre_override = _inspect_config_composition_with_argv_scoped_overlays(
            parsed.base_config_path,
            recipe_catalog=recipe_catalog,
            argv_scoped_overlays=parsed.scoped_overlays,
            overrides=(),
            include_raw_source_snapshots=False,
        )
    except ConfigError:
        return ()

    warnings: list[ConfigArgvWarning] = []
    for override, candidates in candidates_by_override.items():
        if not isinstance(_lookup_dot_path(pre_override.resolved, override.path), Mapping):
            continue
        existing = [candidate for candidate in candidates if candidate.exists]
        warnings.append(
            ConfigArgvWarning(
                code="possible_missing_scoped_overlay_slash",
                message=(
                    "Value override targets an existing mapping and the RHS resolves like "
                    "a scoped overlay source."
                ),
                source_order=override.order,
                token=override.raw,
                path=override.path,
                remediation="Use trailing-slash scoped overlay syntax, for example 'scope/=variant'.",
                details={
                    "rhs": override.value,
                    "candidate_paths": [candidate.path for candidate in candidates],
                    "resolved_candidate_paths": [candidate.path for candidate in existing],
                },
            )
        )
    return tuple(warnings)


def _warning_candidates(base_config_path: str, override: ArgvValueOverride) -> tuple[ScopedOverlayCandidate, ...]:
    value = override.value
    if not isinstance(value, str) or value == "" or value.startswith("~"):
        return ()
    rhs_path = Path(value)
    if rhs_path.is_absolute():
        path = rhs_path.resolve(strict=False)
        return (ScopedOverlayCandidate(path=str(path), origin="absolute", exists=path.is_file()),)

    base_dir = Path(base_config_path).parent.resolve(strict=False)
    scope_path = tuple(segment for segment in override.path.split(".") if segment)
    if not scope_path:
        return ()
    scope_dir = base_dir.joinpath(*scope_path).resolve(strict=False)
    variants = _warning_rhs_variants(rhs_path)
    candidates: list[ScopedOverlayCandidate] = []
    for origin, root in (("scope_directory", scope_dir), ("base_directory", base_dir)):
        for variant in variants:
            path = (root / variant).resolve(strict=False)
            candidates.append(
                ScopedOverlayCandidate(
                    path=str(path),
                    origin=cast(ScopedOverlayCandidateOrigin, origin),
                    exists=path.is_file(),
                )
            )
    return tuple(candidates)


def _warning_rhs_variants(rhs_path: Path) -> tuple[Path, ...]:
    if rhs_path.suffix:
        return (rhs_path,)
    try:
        return (rhs_path.with_suffix(".yaml"), rhs_path.with_suffix(".yml"))
    except ValueError:
        return (rhs_path,)


def _lookup_dot_path(mapping: Mapping[str, PlainData], path: str) -> PlainData | None:
    current: PlainData | None = cast(PlainData, mapping)
    for segment in path.split("."):
        if not isinstance(current, Mapping) or segment not in current:
            return None
        current = current[segment]
    return current


def _validate_config_args_result_common(
    *,
    base_config_path: str,
    parsed_args: ParsedConfigArgs,
    value_overrides: tuple[ArgvValueOverride, ...],
    scoped_overlays: tuple[ArgvScopedOverlay, ...],
    unparsed_args: tuple[ArgvUnparsedArg, ...],
    warnings: tuple[ConfigArgvWarning, ...],
) -> None:
    if base_config_path == "":
        raise ConfigValidationError("config args result base_config_path must be non-empty")
    if not isinstance(parsed_args, ParsedConfigArgs):
        raise ConfigValidationError("parsed_args must be ParsedConfigArgs")
    if base_config_path != parsed_args.base_config_path:
        raise ConfigValidationError("config args result metadata must match parsed_args")
    if tuple(value_overrides) != parsed_args.value_overrides:
        raise ConfigValidationError("value_overrides must mirror parsed_args.value_overrides")
    if tuple(scoped_overlays) != parsed_args.scoped_overlays:
        raise ConfigValidationError("scoped_overlays must mirror parsed_args.scoped_overlays")
    if tuple(unparsed_args) != parsed_args.unparsed_args:
        raise ConfigValidationError("unparsed_args must mirror parsed_args.unparsed_args")
    for index, warning in enumerate(tuple(warnings)):
        if not isinstance(warning, ConfigArgvWarning):
            raise ConfigValidationError(f"warnings[{index}] must be ConfigArgvWarning")


def _config_args_result_metadata_to_dict(
    *,
    base_config_path: str,
    parsed_args: ParsedConfigArgs,
    value_overrides: tuple[ArgvValueOverride, ...],
    scoped_overlays: tuple[ArgvScopedOverlay, ...],
    unparsed_args: tuple[ArgvUnparsedArg, ...],
    warnings: tuple[ConfigArgvWarning, ...],
    base_details: tuple[dict[str, PlainData], ...] = (),
    selected_objects: tuple[dict[str, PlainData], ...] = (),
) -> dict[str, PlainData]:
    return {
        "base_config_path": base_config_path,
        "parsed_args": parsed_args.to_dict(),
        "value_overrides": [override.to_dict() for override in value_overrides],
        "scoped_overlays": [overlay.to_dict() for overlay in scoped_overlays],
        "unparsed_args": [arg.to_dict() for arg in unparsed_args],
        "warnings": [warning.to_dict() for warning in warnings],
        "base_details": list(_normalize_base_details(base_details)),
        "selected_objects": list(_normalize_selected_object_metadata(selected_objects)),
    }


def _normalize_base_details(base_details: tuple[dict[str, PlainData], ...]) -> tuple[dict[str, PlainData], ...]:
    normalized: list[dict[str, PlainData]] = []
    for index, item in enumerate(tuple(base_details)):
        plain_item = ensure_plain_data(item, path=f"base_details[{index}]")
        if not isinstance(plain_item, dict):
            raise ConfigValidationError(f"base_details[{index}] must be a mapping")
        normalized.append(cast(dict[str, PlainData], plain_item))
    return tuple(normalized)


def _normalize_selected_object_specs(
    selected_objects: Sequence[str] | Mapping[str, str],
) -> tuple[dict[str, PlainData], ...]:
    if isinstance(selected_objects, str):
        raise _selected_instantiation_error(
            "selected_objects must be a sequence of dot paths or a mapping of object keys to dot paths",
            code="invalid_selected_objects",
            expected="sequence or mapping",
            actual="str",
            details={"actual_type": "str"},
        )

    specs: list[dict[str, PlainData]] = []
    seen_keys: set[str] = set()
    if isinstance(selected_objects, Mapping):
        raw_items = tuple(selected_objects.items())
        for index, (key, dot_path) in enumerate(raw_items):
            if not isinstance(key, str) or key == "":
                raise _selected_instantiation_error(
                    "selected object keys must be non-empty strings",
                    code="invalid_selected_object_key",
                    expected="non-empty string",
                    actual=type(key).__name__ if not isinstance(key, str) else "empty string",
                    details={"selector_index": index},
                )
            if key in seen_keys:
                raise _selected_instantiation_error(
                    "selected object keys must be unique",
                    code="duplicate_selected_object_key",
                    details={"key": key, "selector_index": index},
                )
            seen_keys.add(key)
            dot_path = _normalize_selected_dot_path(dot_path, key=key, index=index)
            specs.append({"key": key, "path": dot_path})
        return tuple(specs)

    if not isinstance(selected_objects, Sequence):
        raise _selected_instantiation_error(
            "selected_objects must be a sequence of dot paths or a mapping of object keys to dot paths",
            code="invalid_selected_objects",
            expected="sequence or mapping",
            actual=type(selected_objects).__name__,
            details={"actual_type": type(selected_objects).__name__},
        )

    for index, dot_path in enumerate(selected_objects):
        path = _normalize_selected_dot_path(dot_path, key="", index=index)
        if path in seen_keys:
            raise _selected_instantiation_error(
                "selected object keys must be unique",
                code="duplicate_selected_object_key",
                details={"key": path, "selector_index": index},
            )
        seen_keys.add(path)
        specs.append({"key": path, "path": path})
    return tuple(specs)


def _normalize_selected_dot_path(dot_path: object, *, key: str, index: int) -> str:
    if not isinstance(dot_path, str) or dot_path == "":
        raise _selected_instantiation_error(
            "selected object paths must be non-empty dot-path strings",
            code="invalid_selected_object_path",
            expected="non-empty dot path",
            actual=type(dot_path).__name__ if not isinstance(dot_path, str) else "empty string",
            details={"key": key, "selector_index": index},
        )
    segments = dot_path.split(".")
    if any(segment == "" for segment in segments):
        raise _selected_instantiation_error(
            "selected object paths must not contain empty path segments",
            code="invalid_selected_object_path",
            expected="dot path without empty segments",
            actual=dot_path,
            details={"key": key, "path": dot_path, "selector_index": index},
        )
    return dot_path


def _normalize_selected_object_metadata(
    selected_objects: tuple[dict[str, PlainData], ...],
) -> tuple[dict[str, PlainData], ...]:
    normalized: list[dict[str, PlainData]] = []
    seen_keys: set[str] = set()
    for index, item in enumerate(tuple(selected_objects)):
        plain_item = ensure_plain_data(item, path=f"selected_objects[{index}]")
        if not isinstance(plain_item, dict):
            raise ConfigValidationError(f"selected_objects[{index}] must be a mapping")
        key = plain_item.get("key")
        dot_path = plain_item.get("path")
        if not isinstance(key, str) or key == "":
            raise ConfigValidationError(f"selected_objects[{index}].key must be a non-empty string")
        if key in seen_keys:
            raise ConfigValidationError(f"selected_objects[{index}].key must be unique")
        seen_keys.add(key)
        if not isinstance(dot_path, str) or dot_path == "" or any(segment == "" for segment in dot_path.split(".")):
            raise ConfigValidationError(f"selected_objects[{index}].path must be a non-empty dot path")
        normalized.append({"key": key, "path": dot_path})
    return tuple(normalized)


def _instantiate_selected_objects(
    resolved: Mapping[str, PlainData],
    *,
    selected_objects: tuple[dict[str, PlainData], ...],
    runtime: Mapping[str, object] | None,
) -> dict[str, object]:
    selected_values: list[tuple[str, str, PlainData]] = []
    for item in selected_objects:
        key = cast(str, item["key"])
        dot_path = cast(str, item["path"])
        value = _lookup_selected_object_value(resolved, key=key, dot_path=dot_path)
        selected_values.append((key, dot_path, value))

    for _key, dot_path, value in selected_values:
        _ensure_no_unresolved_structural_directives(
            value,
            path=_config_path_for_dot_path(dot_path),
        )

    objects: dict[str, object] = {}
    for key, _dot_path, value in selected_values:
        objects[key] = instantiate(value, runtime=runtime)
    return objects


def _lookup_selected_object_value(mapping: Mapping[str, PlainData], *, key: str, dot_path: str) -> PlainData:
    current: PlainData = cast(PlainData, mapping)
    traversed: list[str] = []
    for segment in dot_path.split("."):
        if not isinstance(current, Mapping):
            traversed_path = ".".join(traversed)
            raise _selected_instantiation_error(
                "Selected object path traversed a non-mapping value",
                code="non_mapping_selected_object_parent",
                config_path=_config_path_for_dot_path(traversed_path),
                expected="mapping",
                actual=type(current).__name__,
                details={
                    "key": key,
                    "path": dot_path,
                    "traversed_path": cast(list[PlainData], list(traversed)),
                },
            )
        if segment not in current:
            raise _selected_instantiation_error(
                "Selected object path does not exist",
                code="missing_selected_object_path",
                config_path=_config_path_for_dot_path(dot_path),
                expected="existing dot path",
                actual="missing",
                details={
                    "key": key,
                    "path": dot_path,
                    "missing_segment": segment,
                    "traversed_path": cast(list[PlainData], list(traversed)),
                },
            )
        current = current[segment]
        traversed.append(segment)
    return current


def _config_path_for_dot_path(dot_path: str) -> str:
    if dot_path == "":
        return "$"
    return f"$.{dot_path}"


def _selected_instantiation_error(
    message: str,
    *,
    code: str,
    config_path: str | None = None,
    expected: PlainData | None = None,
    actual: PlainData | None = None,
    details: dict[str, PlainData] | None = None,
) -> ConfigValidationError:
    return ConfigValidationError(
        message,
        context=ConfigErrorContext(
            code=code,
            source_kind="config_entrypoint",
            source_order=-1,
            source_path="<config-entrypoint>",
            config_path=config_path,
            expected=expected,
            actual=actual,
            directive="selected_instantiation",
            remediation=_selected_instantiation_remediation(code),
            details=details,
        ),
    )


def _selected_instantiation_remediation(code: str) -> str | None:
    if code in {"invalid_selected_objects", "invalid_selected_object_key", "invalid_selected_object_path"}:
        return "Pass selected_objects as dot-path strings or a mapping of object keys to dot paths."
    if code == "duplicate_selected_object_key":
        return "Choose unique selected object keys."
    if code in {"missing_selected_object_path", "non_mapping_selected_object_parent"}:
        return "Select an existing path in the resolved config."
    if code == "invalid_selected_runtime":
        return "Pass runtime as a mapping when selected objects use runtime injection."
    return None


def _validate_argv_result_common(
    *,
    command: str,
    base_config_path: str,
    parsed_argv: ParsedConfigArgv,
    value_overrides: tuple[ArgvValueOverride, ...],
    scoped_overlays: tuple[ArgvScopedOverlay, ...],
    unparsed_args: tuple[ArgvUnparsedArg, ...],
    warnings: tuple[ConfigArgvWarning, ...],
) -> None:
    if command == "":
        raise ConfigValidationError("argv result command must be non-empty")
    if base_config_path == "":
        raise ConfigValidationError("argv result base_config_path must be non-empty")
    if not isinstance(parsed_argv, ParsedConfigArgv):
        raise ConfigValidationError("parsed_argv must be ParsedConfigArgv")
    if command != parsed_argv.command or base_config_path != parsed_argv.base_config_path:
        raise ConfigValidationError("argv result metadata must match parsed_argv")
    if tuple(value_overrides) != parsed_argv.value_overrides:
        raise ConfigValidationError("value_overrides must mirror parsed_argv.value_overrides")
    if tuple(scoped_overlays) != parsed_argv.scoped_overlays:
        raise ConfigValidationError("scoped_overlays must mirror parsed_argv.scoped_overlays")
    if tuple(unparsed_args) != parsed_argv.unparsed_args:
        raise ConfigValidationError("unparsed_args must mirror parsed_argv.unparsed_args")
    for index, warning in enumerate(tuple(warnings)):
        if not isinstance(warning, ConfigArgvWarning):
            raise ConfigValidationError(f"warnings[{index}] must be ConfigArgvWarning")


def _argv_result_metadata_to_dict(
    *,
    command: str,
    base_config_path: str,
    parsed_argv: ParsedConfigArgv,
    value_overrides: tuple[ArgvValueOverride, ...],
    scoped_overlays: tuple[ArgvScopedOverlay, ...],
    unparsed_args: tuple[ArgvUnparsedArg, ...],
    warnings: tuple[ConfigArgvWarning, ...],
) -> dict[str, PlainData]:
    return {
        "command": command,
        "base_config_path": base_config_path,
        "parsed_argv": parsed_argv.to_dict(),
        "value_overrides": [override.to_dict() for override in value_overrides],
        "scoped_overlays": [overlay.to_dict() for overlay in scoped_overlays],
        "unparsed_args": [arg.to_dict() for arg in unparsed_args],
        "warnings": [warning.to_dict() for warning in warnings],
    }


def _composed_config_to_dict(config: ComposedConfig) -> dict[str, PlainData]:
    return {
        "resolved": config.resolved,
        "redacted": config.redacted,
        "unresolved": config.unresolved,
        "provenance": config.provenance.to_dict(),
        "recipe_manifest": list(config.recipe_manifest),
        "fingerprint": config.fingerprint,
        "manifest": config.manifest.to_dict(),
        "source_artifacts": [record.to_dict() for record in config.source_artifacts],
        "fingerprint_records": [record.to_dict() for record in config.fingerprint_records],
        "raw_source_snapshots": config.raw_source_snapshots.to_dict(),
    }


def _inspection_to_dict(inspection: ConfigCompositionInspection) -> dict[str, PlainData]:
    return {
        "stages": [
            {"name": stage.name, "status": stage.status, "payload": stage.payload}
            for stage in inspection.stages
        ],
        "unresolved": inspection.unresolved,
        "resolved": inspection.resolved,
        "redacted": inspection.redacted,
        "provenance": inspection.provenance.to_dict(),
        "recipe_manifest": list(inspection.recipe_manifest),
        "fingerprint": inspection.fingerprint,
        "manifest": inspection.manifest.to_dict(),
        "source_artifacts": [record.to_dict() for record in inspection.source_artifacts],
        "fingerprint_records": [record.to_dict() for record in inspection.fingerprint_records],
        "raw_source_snapshots": inspection.raw_source_snapshots.to_dict(),
    }


def compose_config(
    config_path: str | Path,
    overlays: list[str | Path] | tuple[str | Path, ...] = (),
    overrides: list[str] | tuple[str, ...] = (),
    recipe_catalog: RecipeCatalog | None = None,
    *,
    include_raw_source_snapshots: bool = False,
) -> ComposedConfig:
    from .compose import inspect_config_composition

    if overlays is None:
        raise ConfigValidationError("overlays may not be None")
    if overrides is None:
        raise ConfigValidationError("overrides may not be None")
    if recipe_catalog is not None and not isinstance(recipe_catalog, RecipeCatalog):
        raise ConfigValidationError("recipe_catalog must be a RecipeCatalog")
    if not isinstance(include_raw_source_snapshots, bool):
        raise ConfigValidationError("include_raw_source_snapshots must be a bool")

    return inspect_config_composition(
        config_path=config_path,
        overlays=tuple(overlays),
        overrides=tuple(overrides),
        recipe_catalog=recipe_catalog if recipe_catalog is not None else _get_default_recipe_catalog(),
        include_raw_source_snapshots=include_raw_source_snapshots,
    ).to_composed_config()


def inspect_config_composition(
    config_path: str | Path,
    overlays: list[str | Path] | tuple[str | Path, ...] = (),
    overrides: list[str] | tuple[str, ...] = (),
    recipe_catalog: RecipeCatalog | None = None,
    *,
    include_raw_source_snapshots: bool = False,
) -> ConfigCompositionInspection:
    from .compose import inspect_config_composition as _inspect_config_composition

    if overlays is None:
        raise ConfigValidationError("overlays may not be None")
    if overrides is None:
        raise ConfigValidationError("overrides may not be None")
    if recipe_catalog is not None and not isinstance(recipe_catalog, RecipeCatalog):
        raise ConfigValidationError("recipe_catalog must be a RecipeCatalog")
    if not isinstance(include_raw_source_snapshots, bool):
        raise ConfigValidationError("include_raw_source_snapshots must be a bool")

    return _inspect_config_composition(
        config_path=config_path,
        overlays=tuple(overlays),
        overrides=tuple(overrides),
        recipe_catalog=recipe_catalog if recipe_catalog is not None else _get_default_recipe_catalog(),
        include_raw_source_snapshots=include_raw_source_snapshots,
    )


def compose_config_with_catalog(
    config_path: str | Path,
    *,
    recipe_catalog: RecipeCatalog,
    overlays: list[str | Path] | tuple[str | Path, ...] = (),
    overrides: list[str] | tuple[str, ...] = (),
    include_raw_source_snapshots: bool = False,
) -> ComposedConfig:
    from .compose import inspect_config_composition

    if not isinstance(recipe_catalog, RecipeCatalog):
        raise ConfigValidationError("recipe_catalog must be a RecipeCatalog")
    if overlays is None:
        raise ConfigValidationError("overlays may not be None")
    if overrides is None:
        raise ConfigValidationError("overrides may not be None")
    if not isinstance(include_raw_source_snapshots, bool):
        raise ConfigValidationError("include_raw_source_snapshots must be a bool")

    return inspect_config_composition(
        config_path=config_path,
        overlays=tuple(overlays),
        overrides=tuple(overrides),
        recipe_catalog=recipe_catalog,
        include_raw_source_snapshots=include_raw_source_snapshots,
    ).to_composed_config()


def instantiate(value: object, *, runtime: Mapping[str, object] | None = None) -> object:
    from .instantiate.recursive import instantiate as _instantiate

    return _instantiate(value=value, runtime=runtime)


def register_recipe(name: str, recipe: RecipeImplementation, *, replace: bool = False) -> None:
    _get_default_recipe_catalog().register(name=name, recipe=recipe, replace=replace)


def _get_default_recipe_catalog() -> RecipeCatalog:
    global __default_recipe_catalog
    if __default_recipe_catalog is None:
        __default_recipe_catalog = RecipeCatalog()
    return __default_recipe_catalog


__all__ = [
    "ArgvScopedOverlay",
    "ArgvUnparsedArg",
    "ArgvValueOverride",
    "ComposedConfig",
    "ConfigArgsCompositionResult",
    "ConfigArgsInspectionResult",
    "ConfigBaseRequest",
    "ConfigBaseResolution",
    "ConfigEntrypoint",
    "ConfigArgvCompositionResult",
    "ConfigArgvInspectionResult",
    "ConfigArgvWarning",
    "ConfigCompositionInspection",
    "ConfigCompositionStageRecord",
    "ParsedConfigArgs",
    "ParsedConfigArgv",
    "ScopedOverlayCandidate",
    "compose_config",
    "compose_config_from_args",
    "compose_config_from_argv",
    "inspect_config_composition",
    "inspect_config_args",
    "inspect_config_from_argv",
    "compose_config_with_catalog",
    "compare_config_artifact_fingerprints",
    "ConfigFingerprintComparison",
    "RawSourceSnapshotBundle",
    "RawSourceSnapshotPayload",
    "RawSourceSnapshotReference",
    "StructuralResolutionRecord",
    "StructuralResolutionRequest",
    "StructuralResolutionResult",
    "StructuralResolverDefinition",
    "StructuralResolverRejected",
    "ARTIFACT_SAFE_FINGERPRINT_LABEL",
    "ARTIFACT_SAFE_FINGERPRINT_POLICY",
    "ARTIFACT_SAFE_RUNTIME_REPLAY",
    "instantiate",
    "register_recipe",
    "resolve_structural",
]
