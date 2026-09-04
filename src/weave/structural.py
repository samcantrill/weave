"""Call-scoped structural resolution for composed plain config values."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal, cast

from .errors import (
    ConfigErrorContext,
    ConfigStructuralResolutionError,
    ConfigValidationError,
    StructuralResolverRejected,
)
from .plain import (
    PlainData,
    ensure_plain_data,
    freeze_plain_data,
    thaw_plain_data,
)
from .redaction import REDACTION_MARKER, is_secret_path, redact_secrets
from .source_maps import ConfigPath, format_config_path

STRUCTURAL_RESOLUTION_SCHEMA_VERSION = 1
STRUCTURAL_RESOLUTION_DIRECTIVE = "_resolve_"

StructuralOutputKind = Literal[
    "null",
    "boolean",
    "integer",
    "float",
    "string",
    "list",
    "mapping",
]

_RESOLVER_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*(?:\.[A-Za-z][A-Za-z0-9_-]*)+$")
_OUTPUT_KINDS = frozenset({"null", "boolean", "integer", "float", "string", "list", "mapping"})


@dataclass(frozen=True, slots=True)
class StructuralResolutionRequest:
    """Immutable arguments and location supplied to one resolver call."""

    config_path: str
    resolver: str
    version: int
    arguments: Mapping[str, object] = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.config_path, str) or not self.config_path.startswith("$"):
            raise ConfigValidationError("StructuralResolutionRequest.config_path must be a config path")
        if not _valid_resolver_name(self.resolver):
            raise ConfigValidationError("StructuralResolutionRequest.resolver must be a namespaced resolver name")
        if type(self.version) is not int or self.version <= 0:
            raise ConfigValidationError("StructuralResolutionRequest.version must be a positive integer")
        try:
            frozen = freeze_plain_data(
                self.arguments,
                path=f"{self.config_path}.{STRUCTURAL_RESOLUTION_DIRECTIVE}",
            )
        except Exception as exc:  # noqa: BLE001
            raise ConfigValidationError("StructuralResolutionRequest.arguments must be a plain-data mapping") from exc
        if not isinstance(frozen, Mapping):
            raise ConfigValidationError("StructuralResolutionRequest.arguments must be a mapping")
        object.__setattr__(self, "arguments", frozen)


@dataclass(frozen=True, slots=True)
class StructuralResolverDefinition:
    """One exact resolver version and its call-scoped handler."""

    version: int
    handler: Callable[[StructuralResolutionRequest], object] = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version <= 0:
            raise ConfigValidationError("StructuralResolverDefinition.version must be a positive integer")
        if not callable(self.handler):
            raise ConfigValidationError("StructuralResolverDefinition.handler must be callable")


@dataclass(frozen=True, slots=True)
class StructuralResolutionRecord:
    """Artifact-safe record of one successful structural resolution."""

    schema_version: int
    order: int
    config_path: str
    resolver: str
    resolver_version: int
    arguments: Mapping[str, PlainData] | str
    output_kind: StructuralOutputKind
    status: Literal["resolved"] = "resolved"

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not int
            or self.schema_version != STRUCTURAL_RESOLUTION_SCHEMA_VERSION
        ):
            raise ConfigValidationError("StructuralResolutionRecord.schema_version is unsupported")
        if type(self.order) is not int or self.order < 0:
            raise ConfigValidationError("StructuralResolutionRecord.order must be a non-negative integer")
        if not isinstance(self.config_path, str) or not self.config_path.startswith("$"):
            raise ConfigValidationError("StructuralResolutionRecord.config_path must be a config path")
        if not _valid_resolver_name(self.resolver):
            raise ConfigValidationError("StructuralResolutionRecord.resolver must be a namespaced resolver name")
        if type(self.resolver_version) is not int or self.resolver_version <= 0:
            raise ConfigValidationError("StructuralResolutionRecord.resolver_version must be a positive integer")
        if self.output_kind not in _OUTPUT_KINDS:
            raise ConfigValidationError("StructuralResolutionRecord.output_kind is unsupported")
        if self.status != "resolved":
            raise ConfigValidationError("StructuralResolutionRecord.status must be 'resolved'")

        if isinstance(self.arguments, str):
            if self.arguments != REDACTION_MARKER:
                raise ConfigValidationError("StructuralResolutionRecord.arguments string must be the redaction marker")
            return
        try:
            normalized_arguments = ensure_plain_data(
                self.arguments,
                path="StructuralResolutionRecord.arguments",
            )
        except Exception as exc:  # noqa: BLE001
            raise ConfigValidationError("StructuralResolutionRecord.arguments must be a plain-data mapping") from exc
        if not isinstance(normalized_arguments, dict):
            raise ConfigValidationError("StructuralResolutionRecord.arguments must be a mapping")
        if is_secret_path(self.config_path):
            object.__setattr__(self, "arguments", REDACTION_MARKER)
            return
        frozen = freeze_plain_data(
            redact_secrets(normalized_arguments),
            path="StructuralResolutionRecord.arguments",
        )
        object.__setattr__(self, "arguments", frozen)

    def to_dict(self) -> dict[str, PlainData]:
        """Return a detached plain-data representation."""

        arguments: PlainData
        if isinstance(self.arguments, str):
            arguments = self.arguments
        else:
            arguments = thaw_plain_data(
                self.arguments,
                path="StructuralResolutionRecord.arguments",
            )
        return {
            "schema_version": self.schema_version,
            "order": self.order,
            "config_path": self.config_path,
            "resolver": self.resolver,
            "resolver_version": self.resolver_version,
            "arguments": arguments,
            "output_kind": self.output_kind,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> StructuralResolutionRecord:
        """Rebuild a record from its exact plain-data schema."""

        try:
            payload = ensure_plain_data(value, path="StructuralResolutionRecord")
        except Exception as exc:  # noqa: BLE001
            raise ConfigValidationError("StructuralResolutionRecord payload must be plain data") from exc
        if not isinstance(payload, dict):
            raise ConfigValidationError("StructuralResolutionRecord payload must be a mapping")
        expected_fields = {
            "schema_version",
            "order",
            "config_path",
            "resolver",
            "resolver_version",
            "arguments",
            "output_kind",
            "status",
        }
        if set(payload) != expected_fields:
            raise ConfigValidationError("StructuralResolutionRecord payload has missing or unknown fields")

        output_kind = payload["output_kind"]
        status = payload["status"]
        arguments = payload["arguments"]
        if not isinstance(output_kind, str):
            raise ConfigValidationError("StructuralResolutionRecord.output_kind must be a string")
        if not isinstance(status, str):
            raise ConfigValidationError("StructuralResolutionRecord.status must be a string")
        if not isinstance(arguments, (dict, str)):
            raise ConfigValidationError("StructuralResolutionRecord.arguments must be a mapping or redaction marker")
        return cls(
            schema_version=cast(int, payload["schema_version"]),
            order=cast(int, payload["order"]),
            config_path=cast(str, payload["config_path"]),
            resolver=cast(str, payload["resolver"]),
            resolver_version=cast(int, payload["resolver_version"]),
            arguments=arguments,
            output_kind=cast(StructuralOutputKind, output_kind),
            status=cast(Literal["resolved"], status),
        )


@dataclass(frozen=True, slots=True)
class StructuralResolutionResult:
    """Detached executable value and ordered artifact-safe records."""

    value: PlainData = field(repr=False)
    records: tuple[StructuralResolutionRecord, ...]

    def __post_init__(self) -> None:
        try:
            normalized = ensure_plain_data(
                self.value,
                path="StructuralResolutionResult.value",
            )
        except Exception as exc:  # noqa: BLE001
            raise ConfigValidationError("StructuralResolutionResult.value must be plain data") from exc
        records = tuple(self.records)
        if any(not isinstance(record, StructuralResolutionRecord) for record in records):
            raise ConfigValidationError("StructuralResolutionResult.records must contain structural resolution records")
        if any(record.order != index for index, record in enumerate(records)):
            raise ConfigValidationError("StructuralResolutionResult.records must use contiguous execution order")
        object.__setattr__(self, "value", normalized)
        object.__setattr__(self, "records", records)


@dataclass(frozen=True, slots=True)
class _Directive:
    path: ConfigPath
    resolver: str
    version: int
    declared_arguments: dict[str, PlainData]
    dependencies: frozenset[ConfigPath]


def resolve_structural(
    value: object,
    *,
    resolvers: Mapping[str, StructuralResolverDefinition],
) -> StructuralResolutionResult:
    """Resolve configured ``_resolve_`` envelopes without mutating ``value``.

    Resolver definitions are supplied only for this call. All directive shapes,
    resolver names, versions, and nested dependencies are validated before the
    first handler runs. Handlers receive immutable arguments and must return
    finite plain data. Returned ``_resolve_`` directives are rejected rather
    than executed dynamically.
    """

    definitions = _normalize_resolver_definitions(resolvers)
    source = _normalize_plain_value(
        value,
        config_path="$",
        phase="input",
        completed_resolution_count=0,
    )
    directives = _scan_directives(source, definitions=definitions)
    ordered = _order_directives(directives)

    working = source
    records: list[StructuralResolutionRecord] = []
    for directive in ordered:
        current = _lookup_path(working, directive.path)
        if not isinstance(current, dict):  # pragma: no cover - internal invariant
            raise AssertionError("planned structural directive is no longer a mapping")
        envelope = current[STRUCTURAL_RESOLUTION_DIRECTIVE]
        if not isinstance(envelope, dict):  # pragma: no cover - preflight owns this
            raise AssertionError("planned structural directive envelope is no longer a mapping")
        arguments = {key: child for key, child in envelope.items() if key not in {"resolver", "version"}}
        request = StructuralResolutionRequest(
            config_path=format_config_path(directive.path),
            resolver=directive.resolver,
            version=directive.version,
            arguments=arguments,
        )
        definition = definitions[directive.resolver]

        raw_output: object = None
        resolution_error: ConfigStructuralResolutionError | None = None
        try:
            raw_output = definition.handler(request)
        except StructuralResolverRejected as exc:
            rejection_details: PlainData
            if is_secret_path(directive.path):
                rejection_details = REDACTION_MARKER
            else:
                rejection_details = redact_secrets(exc.details)
            resolution_error = _structural_error(
                "Structural resolver rejected its request",
                code="structural_resolver_rejected",
                config_path=format_config_path(directive.path),
                details={
                    "resolver": directive.resolver,
                    "resolver_version": directive.version,
                    "rejection_code": exc.code,
                    "rejection_details": rejection_details,
                    "completed_resolution_count": len(records),
                },
            )
        except Exception as exc:  # noqa: BLE001
            resolution_error = _structural_error(
                "Structural resolver failed",
                code="structural_resolver_failed",
                config_path=format_config_path(directive.path),
                details={
                    "resolver": directive.resolver,
                    "resolver_version": directive.version,
                    "exception_type": type(exc).__name__,
                    "completed_resolution_count": len(records),
                },
            )

        # Raise only after leaving the resolver's exception handler. ``from
        # None`` suppresses display but still retains the original exception in
        # ``__context__``, where telemetry could recover its raw message or
        # resolver-owned details.
        if resolution_error is not None:
            raise resolution_error

        output = _normalize_plain_value(
            raw_output,
            config_path=format_config_path(directive.path),
            phase="resolver_output",
            completed_resolution_count=len(records),
        )
        unresolved_path = _find_unresolved_path(output, path=directive.path)
        if unresolved_path is not None:
            raise _structural_error(
                "Structural resolver returned an unresolved directive",
                code="unresolved_structural_output",
                config_path=format_config_path(unresolved_path),
                details={
                    "resolver": directive.resolver,
                    "resolver_version": directive.version,
                    "originating_config_path": format_config_path(directive.path),
                    "completed_resolution_count": len(records),
                },
            )

        working = _replace_path(working, path=directive.path, replacement=output)
        records.append(
            StructuralResolutionRecord(
                schema_version=STRUCTURAL_RESOLUTION_SCHEMA_VERSION,
                order=len(records),
                config_path=format_config_path(directive.path),
                resolver=directive.resolver,
                resolver_version=directive.version,
                arguments=_redacted_arguments(
                    directive.declared_arguments,
                    path=directive.path,
                ),
                output_kind=_output_kind(output),
            )
        )

    unresolved_path = _find_unresolved_path(working, path=())
    if unresolved_path is not None:  # pragma: no cover - scan/output checks own this
        raise _structural_error(
            "Structural resolution left an unresolved directive",
            code="unresolved_structural_output",
            config_path=format_config_path(unresolved_path),
            details={"completed_resolution_count": len(records)},
        )

    return StructuralResolutionResult(value=working, records=tuple(records))


def _ensure_no_unresolved_structural_directives(
    value: object,
    *,
    path: str = "$",
) -> None:
    """Fail before target construction if ``value`` contains ``_resolve_``."""

    _preflight_unresolved(value, path=path, active={})


def _normalize_resolver_definitions(
    resolvers: Mapping[str, StructuralResolverDefinition],
) -> dict[str, StructuralResolverDefinition]:
    if not isinstance(resolvers, Mapping):
        raise _structural_error(
            "Structural resolvers must be supplied as a mapping",
            code="invalid_structural_resolvers",
            config_path="$",
            expected="mapping of names to StructuralResolverDefinition",
            actual=type(resolvers).__name__,
        )

    normalized: dict[str, StructuralResolverDefinition] = {}
    for name, definition in resolvers.items():
        if not isinstance(name, str) or not _valid_resolver_name(name):
            raise _structural_error(
                "Structural resolver names must be namespaced",
                code="invalid_structural_resolver_name",
                config_path="$",
                expected="namespaced resolver name",
                actual=type(name).__name__ if not isinstance(name, str) else "invalid name",
            )
        if name == "weave" or name.startswith("weave."):
            raise _structural_error(
                "The weave resolver namespace is reserved",
                code="reserved_structural_resolver_name",
                config_path="$",
                details={"resolver": name},
            )
        if not isinstance(definition, StructuralResolverDefinition):
            raise _structural_error(
                "Structural resolver definitions must use StructuralResolverDefinition",
                code="invalid_structural_resolver_definition",
                config_path="$",
                expected="StructuralResolverDefinition",
                actual=type(definition).__name__,
                details={"resolver": name},
            )
        normalized[name] = definition
    return normalized


def _normalize_plain_value(
    value: object,
    *,
    config_path: str,
    phase: Literal["input", "resolver_output"],
    completed_resolution_count: int,
) -> PlainData:
    _ensure_acyclic(
        value,
        path=config_path,
        active={},
        phase=phase,
        completed_resolution_count=completed_resolution_count,
    )
    try:
        return ensure_plain_data(value, path=config_path)
    except Exception as exc:  # noqa: BLE001
        code = "structural_input_not_plain_data" if phase == "input" else "structural_resolver_output_not_plain_data"
        raise _structural_error(
            "Structural resolution requires finite plain data",
            code=code,
            config_path=config_path,
            expected="finite plain data",
            actual=type(value).__name__,
            details={
                "phase": phase,
                "exception_type": type(exc).__name__,
                "completed_resolution_count": completed_resolution_count,
            },
        ) from None


def _ensure_acyclic(
    value: object,
    *,
    path: str,
    active: dict[int, str],
    phase: str,
    completed_resolution_count: int,
) -> None:
    if not _is_container(value):
        return

    identity = id(value)
    if identity in active:
        raise _structural_error(
            "Structural resolution does not support cyclic values",
            code="structural_resolution_cycle",
            config_path=path,
            expected="acyclic value",
            actual="cycle",
            details={
                "phase": phase,
                "referenced_path": active[identity],
                "completed_resolution_count": completed_resolution_count,
            },
        )

    active[identity] = path
    try:
        if isinstance(value, Mapping):
            for key in sorted(value, key=lambda item: str(item)):
                _ensure_acyclic(
                    value[key],
                    path=_child_display_path(path, key),
                    active=active,
                    phase=phase,
                    completed_resolution_count=completed_resolution_count,
                )
        else:
            for index, child in enumerate(cast(Sequence[object], value)):
                _ensure_acyclic(
                    child,
                    path=f"{path}[{index}]",
                    active=active,
                    phase=phase,
                    completed_resolution_count=completed_resolution_count,
                )
    finally:
        del active[identity]


def _scan_directives(
    value: PlainData,
    *,
    definitions: Mapping[str, StructuralResolverDefinition],
) -> dict[ConfigPath, _Directive]:
    directives: dict[ConfigPath, _Directive] = {}

    def visit(node: PlainData, *, path: ConfigPath) -> set[ConfigPath]:
        if isinstance(node, dict):
            if STRUCTURAL_RESOLUTION_DIRECTIVE in node:
                return _scan_directive_node(
                    node,
                    path=path,
                    definitions=definitions,
                    directives=directives,
                    visit=visit,
                )

            found: set[ConfigPath] = set()
            for key in sorted(node):
                found.update(visit(node[key], path=path + (key,)))
            return found

        if isinstance(node, list):
            found = set()
            for index, child in enumerate(node):
                found.update(visit(child, path=path + (index,)))
            return found

        return set()

    visit(value, path=())
    return directives


def _scan_directive_node(
    node: dict[str, PlainData],
    *,
    path: ConfigPath,
    definitions: Mapping[str, StructuralResolverDefinition],
    directives: dict[ConfigPath, _Directive],
    visit: Callable[..., set[ConfigPath]],
) -> set[ConfigPath]:
    config_path = format_config_path(path)
    if set(node) != {STRUCTURAL_RESOLUTION_DIRECTIVE}:
        raise _structural_error(
            "A structural directive may not have sibling fields",
            code="ambiguous_structural_directive",
            config_path=config_path,
            expected="mapping containing only _resolve_",
            actual="_resolve_ with sibling fields",
        )

    envelope = node[STRUCTURAL_RESOLUTION_DIRECTIVE]
    if not isinstance(envelope, dict):
        raise _structural_error(
            "The _resolve_ directive must contain a mapping",
            code="invalid_structural_directive",
            config_path=config_path,
            expected="mapping",
            actual=type(envelope).__name__,
        )
    if "resolver" not in envelope or "version" not in envelope:
        raise _structural_error(
            "The _resolve_ directive requires resolver and version fields",
            code="invalid_structural_directive",
            config_path=config_path,
            expected="resolver and version fields",
            actual="missing required fields",
        )
    if STRUCTURAL_RESOLUTION_DIRECTIVE in envelope:
        raise _structural_error(
            "The _resolve_ envelope may not redefine its directive key",
            code="invalid_structural_directive",
            config_path=config_path,
            actual="reserved argument name",
        )

    resolver = envelope["resolver"]
    version = envelope["version"]
    if not isinstance(resolver, str) or not _valid_resolver_name(resolver):
        raise _structural_error(
            "The _resolve_.resolver field must be a namespaced name",
            code="invalid_structural_resolver_name",
            config_path=config_path,
            expected="namespaced resolver name",
            actual=type(resolver).__name__ if not isinstance(resolver, str) else "invalid name",
        )
    if resolver == "weave" or resolver.startswith("weave."):
        raise _structural_error(
            "The weave resolver namespace is reserved",
            code="reserved_structural_resolver_name",
            config_path=config_path,
            details={"resolver": resolver},
        )
    if type(version) is not int or version <= 0:
        raise _structural_error(
            "The _resolve_.version field must be a positive integer",
            code="invalid_structural_resolver_version",
            config_path=config_path,
            expected="positive integer",
            actual=type(version).__name__,
        )

    definition = definitions.get(resolver)
    if definition is None:
        raise _structural_error(
            "No call-scoped implementation was supplied for the structural resolver",
            code="unknown_structural_resolver",
            config_path=config_path,
            details={
                "resolver": resolver,
                "resolver_version": version,
                "available_resolvers": sorted(definitions),
            },
        )
    if version != definition.version:
        raise _structural_error(
            "The structural resolver version does not match its implementation",
            code="structural_resolver_version_mismatch",
            config_path=config_path,
            expected=definition.version,
            actual=version,
            details={"resolver": resolver},
        )

    arguments = {key: child for key, child in envelope.items() if key not in {"resolver", "version"}}
    declared_arguments = ensure_plain_data(
        arguments,
        path=f"{config_path}.{STRUCTURAL_RESOLUTION_DIRECTIVE}",
    )
    if not isinstance(declared_arguments, dict):  # pragma: no cover - literal mapping
        raise AssertionError("structural resolver arguments must remain a mapping")
    dependencies: set[ConfigPath] = set()
    for key in sorted(arguments):
        dependencies.update(
            visit(
                arguments[key],
                path=path + (STRUCTURAL_RESOLUTION_DIRECTIVE, key),
            )
        )
    directives[path] = _Directive(
        path=path,
        resolver=resolver,
        version=version,
        declared_arguments=declared_arguments,
        dependencies=frozenset(dependencies),
    )
    return dependencies | {path}


def _order_directives(
    directives: Mapping[ConfigPath, _Directive],
) -> tuple[_Directive, ...]:
    pending = {path: set(directive.dependencies) for path, directive in directives.items()}
    ordered: list[_Directive] = []

    while pending:
        ready = sorted(
            (path for path, dependencies in pending.items() if not dependencies),
            key=_path_sort_key,
        )
        if not ready:
            raise _structural_error(
                "Structural resolver dependencies contain a cycle",
                code="structural_dependency_cycle",
                config_path="$",
                details={"remaining_paths": [format_config_path(path) for path in sorted(pending, key=_path_sort_key)]},
            )

        selected = ready[0]
        ordered.append(directives[selected])
        del pending[selected]
        for dependencies in pending.values():
            dependencies.discard(selected)

    return tuple(ordered)


def _lookup_path(value: PlainData, path: ConfigPath) -> PlainData:
    current = value
    for segment in path:
        if isinstance(segment, int):
            if not isinstance(current, list):  # pragma: no cover - planned path
                raise AssertionError("structural path parent is not a list")
            current = current[segment]
        else:
            if not isinstance(current, dict):  # pragma: no cover - planned path
                raise AssertionError("structural path parent is not a mapping")
            current = current[segment]
    return current


def _replace_path(
    value: PlainData,
    *,
    path: ConfigPath,
    replacement: PlainData,
) -> PlainData:
    if not path:
        return replacement

    parent = _lookup_path(value, path[:-1])
    final = path[-1]
    if isinstance(final, int):
        if not isinstance(parent, list):  # pragma: no cover - planned path
            raise AssertionError("structural replacement parent is not a list")
        parent[final] = replacement
    else:
        if not isinstance(parent, dict):  # pragma: no cover - planned path
            raise AssertionError("structural replacement parent is not a mapping")
        parent[final] = replacement
    return value


def _find_unresolved_path(
    value: PlainData,
    *,
    path: ConfigPath,
) -> ConfigPath | None:
    if isinstance(value, dict):
        if STRUCTURAL_RESOLUTION_DIRECTIVE in value:
            return path
        for key in sorted(value):
            found = _find_unresolved_path(value[key], path=path + (key,))
            if found is not None:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _find_unresolved_path(child, path=path + (index,))
            if found is not None:
                return found
    return None


def _preflight_unresolved(
    value: object,
    *,
    path: str,
    active: dict[int, str],
) -> None:
    if not _is_container(value):
        return

    identity = id(value)
    if identity in active:
        raise _structural_error(
            "Target construction input contains a cycle",
            code="structural_resolution_cycle",
            config_path=path,
            expected="acyclic value",
            actual="cycle",
            details={
                "phase": "target_preflight",
                "referenced_path": active[identity],
            },
        )

    active[identity] = path
    try:
        if isinstance(value, Mapping):
            if STRUCTURAL_RESOLUTION_DIRECTIVE in value:
                raise _structural_error(
                    "Target construction received an unresolved structural directive",
                    code="unresolved_structural_directive",
                    config_path=path,
                )
            for key in sorted(value, key=lambda item: str(item)):
                _preflight_unresolved(
                    value[key],
                    path=_child_display_path(path, key),
                    active=active,
                )
        else:
            for index, child in enumerate(cast(Sequence[object], value)):
                _preflight_unresolved(
                    child,
                    path=f"{path}[{index}]",
                    active=active,
                )
    finally:
        del active[identity]


def _redacted_arguments(
    arguments: Mapping[str, PlainData],
    *,
    path: ConfigPath,
) -> Mapping[str, PlainData] | str:
    if is_secret_path(path):
        return REDACTION_MARKER
    return redact_secrets(arguments)


def _output_kind(value: PlainData) -> StructuralOutputKind:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    return "mapping"


def _is_container(value: object) -> bool:
    return isinstance(value, Mapping) or (
        isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
    )


def _valid_resolver_name(value: object) -> bool:
    return isinstance(value, str) and _RESOLVER_NAME_PATTERN.fullmatch(value) is not None


def _path_sort_key(path: ConfigPath) -> tuple[tuple[str, str], ...]:
    return tuple(("index", f"{segment:020d}") if isinstance(segment, int) else ("key", segment) for segment in path)


def _child_display_path(path: str, key: object) -> str:
    if isinstance(key, str):
        if key.isidentifier():
            return f"{path}.{key}"
        escaped = key.replace("\\", r"\\").replace("'", r"\'")
        return f"{path}['{escaped}']"
    return f"{path}[<non-string-key>]"


def _structural_error(
    message: str,
    *,
    code: str,
    config_path: str,
    expected: PlainData | None = None,
    actual: PlainData | None = None,
    details: Mapping[str, object] | None = None,
) -> ConfigStructuralResolutionError:
    normalized_details = ensure_plain_data(
        {"stage": "structural_resolution", **dict(details or {})},
        path="structural_resolution_error.details",
    )
    if not isinstance(normalized_details, dict):  # pragma: no cover - literal mapping
        raise AssertionError("structural error details must remain a mapping")
    return ConfigStructuralResolutionError(
        message,
        context=ConfigErrorContext(
            code=code,
            source_kind="structural_resolution",
            source_order=0,
            source_path="<structural-resolution>",
            config_path=config_path,
            expected=expected,
            actual=actual,
            directive=STRUCTURAL_RESOLUTION_DIRECTIVE,
            remediation=_structural_remediation(code),
            details=normalized_details,
        ),
    )


def _structural_remediation(code: str) -> str | None:
    if code == "unknown_structural_resolver":
        return "Supply the named resolver implementation in this resolve_structural() call."
    if code == "structural_resolver_version_mismatch":
        return "Use the exact resolver version declared by the call-scoped implementation."
    if code in {
        "invalid_structural_directive",
        "ambiguous_structural_directive",
        "invalid_structural_resolver_name",
        "invalid_structural_resolver_version",
    }:
        return "Author one _resolve_ envelope with a namespaced resolver and positive integer version."
    if code in {"structural_resolution_cycle", "structural_dependency_cycle"}:
        return "Remove cyclic values or dependencies from the structural resolution input."
    if code == "unresolved_structural_directive":
        return "Call resolve_structural() after composition and before target construction."
    if code == "unresolved_structural_output":
        return "Return final plain data; resolver handlers may not create new _resolve_ directives."
    if code in {
        "structural_input_not_plain_data",
        "structural_resolver_output_not_plain_data",
    }:
        return "Use finite plain values: null, booleans, numbers, strings, lists, and string-keyed mappings."
    if code in {"structural_resolver_rejected", "structural_resolver_failed"}:
        return "Correct the resolver arguments or supply the required runtime authorities."
    return None


__all__ = [
    "STRUCTURAL_RESOLUTION_DIRECTIVE",
    "STRUCTURAL_RESOLUTION_SCHEMA_VERSION",
    "StructuralResolutionRecord",
    "StructuralResolutionRequest",
    "StructuralResolutionResult",
    "StructuralResolverDefinition",
    "StructuralResolverRejected",
    "resolve_structural",
]
