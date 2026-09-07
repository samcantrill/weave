"""Integration coverage for interpolation and structural resolver boundaries."""

import os
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from types import MappingProxyType
from pathlib import Path

import pytest
from omegaconf import OmegaConf
from omegaconf.resolvers import oc as omegaconf_oc

from weave import (
    ConfigEntrypoint,
    RecipeCatalog,
    compose_config_from_args,
    compose_config_from_argv,
    compose_config_with_catalog,
    inspect_config_args,
    inspect_config_composition,
    StructuralResolutionRequest,
    StructuralResolverDefinition,
    compose_config,
    resolve_structural,
)
from weave.api import inspect_config_from_argv
from weave.errors import ConfigIncludeResolutionError, ConfigUnsupportedResolverError
from weave.redaction import REDACTION_MARKER


def test_public_compose_resolves_oc_env_in_runtime(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(
        "name: base\n"
        "paths:\n"
        "  root: ${oc.env:PHASE8_COMPOSE_ROOT}\n"
        "pipeline:\n"
        "  data: ${paths.root}/value\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PHASE8_COMPOSE_ROOT", "/tmp/phase8-root")

    composed = compose_config(base)
    pipeline = composed.resolved["pipeline"]
    assert isinstance(pipeline, dict)
    assert pipeline["data"] == "/tmp/phase8-root/value"


def test_public_compose_uses_weave_owned_oc_env_when_global_resolver_replaced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(
        "name: base\n"
        "paths:\n"
        "  root: ${oc.env:PHASE8_COMPOSE_ROOT}\n"
        "pipeline:\n"
        "  data: ${paths.root}/value\n",
        encoding="utf-8",
    )
    called: list[str] = []

    def replaced_oc_env(value: str) -> str:
        called.append(value)
        return "/tmp/global-replacement"

    monkeypatch.setenv("PHASE8_COMPOSE_ROOT", "/tmp/weave-owned-root")
    OmegaConf.register_new_resolver("oc.env", replaced_oc_env, replace=True)
    try:
        composed = compose_config(base)
    finally:
        OmegaConf.register_new_resolver("oc.env", omegaconf_oc.env, replace=True)

    pipeline = composed.resolved["pipeline"]
    assert isinstance(pipeline, dict)
    assert pipeline["data"] == "/tmp/weave-owned-root/value"
    assert called == []


def test_public_compose_rejects_non_allowlisted_builtin_resolver(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text("name: base\npipeline:\n  value: ${oc.create:dict}\n", encoding="utf-8")

    with pytest.raises(ConfigUnsupportedResolverError) as exc:
        compose_config(base)

    context = exc.value.context
    assert context is not None
    assert context.code == "unsupported_resolver"
    assert context.actual == "oc.create"


def test_public_compose_rejects_user_resolver_expression(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text("name: base\npipeline:\n  value: ${custom:HOME}\n", encoding="utf-8")

    with pytest.raises(ConfigUnsupportedResolverError) as exc:
        compose_config(base)

    context = exc.value.context
    assert context is not None
    assert context.code == "unsupported_resolver"
    assert context.actual == "custom"


def test_public_compose_attributes_overlay_authored_resolver_error(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    overlay = tmp_path / "overlay.yaml"
    base.write_text("name: base\npipeline:\n  value: base\n", encoding="utf-8")
    overlay.write_text("pipeline:\n  value: ${custom:HOME}\n", encoding="utf-8")

    with pytest.raises(ConfigUnsupportedResolverError) as exc:
        compose_config(base, overlays=(overlay,))

    context = exc.value.context
    assert context is not None
    assert context.source_kind == "overlay"
    assert context.source_path == str(overlay)
    assert context.source_order == 1
    assert context.config_path == "$.pipeline.value"
    assert context.details is not None
    assert context.details["authorship_missing"] is False


def test_public_compose_attributes_override_authored_resolver_error_without_raw_secret(
    tmp_path: Path,
) -> None:
    base = tmp_path / "base.yaml"
    base.write_text("name: base\npipeline:\n  token: base\n", encoding="utf-8")

    with pytest.raises(ConfigUnsupportedResolverError) as exc:
        compose_config(base, overrides=("pipeline.token=${custom:SECRET_VALUE}",))

    context = exc.value.context
    assert context is not None
    assert context.source_kind == "ordinary_override"
    assert context.source_path == "<override>"
    assert context.config_path == "$.pipeline.token"
    assert context.details is not None
    serialized = str(context.to_dict())
    assert context.details["authored_expression"] == REDACTION_MARKER
    assert "SECRET_VALUE" not in serialized
    assert "pipeline.token=${custom:SECRET_VALUE}" not in serialized


def test_public_compose_rejects_include_target_resolver_expression(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(
        "pipeline:\n"
        "  model:\n"
        "    _include_: ${oc.env:PHASE8_INCLUDE}\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigIncludeResolutionError) as exc:
        compose_config(base)

    context = exc.value.context
    assert context is not None
    assert context.code == "resolver_dependent"
    assert context.details is not None
    assert context.details["reason"] == "interpolation_token"


def test_structural_resolution_runs_after_composition_without_changing_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = tmp_path / "base.yaml"
    overlay = tmp_path / "overlay.yaml"
    base.write_text(
        "root: /base\n"
        "manifest:\n"
        "  _resolve_:\n"
        "    resolver: example.runtime\n"
        "    version: 1\n"
        "    path: ${root}/manifest.json\n"
        "    api_token: ${oc.env:STRUCTURAL_API_TOKEN}\n"
        "    kind: base\n",
        encoding="utf-8",
    )
    overlay.write_text("root: /overlay\n", encoding="utf-8")
    monkeypatch.setenv("STRUCTURAL_API_TOKEN", "runtime-token")
    composed = compose_config(
        base,
        overlays=(overlay,),
        overrides=("manifest._resolve_.kind=dataset_manifest",),
    )
    authored_value = deepcopy(composed.resolved)
    authored_fingerprint = composed.fingerprint
    authored_manifest = composed.manifest
    observed_arguments: dict[str, object] = {}

    def resolve_manifest(request: StructuralResolutionRequest) -> str:
        observed_arguments.update(request.arguments)
        return str(request.arguments["path"])

    result = resolve_structural(
        composed.resolved,
        resolvers={
            "example.runtime": StructuralResolverDefinition(
                version=1,
                handler=resolve_manifest,
            )
        },
    )

    assert observed_arguments == {
        "path": "/overlay/manifest.json",
        "api_token": "runtime-token",
        "kind": "dataset_manifest",
    }
    assert result.value["manifest"] == "/overlay/manifest.json"
    assert result.records[0].to_dict()["arguments"] == {
        "path": "/overlay/manifest.json",
        "api_token": REDACTION_MARKER,
        "kind": "dataset_manifest",
    }
    assert composed.resolved == authored_value
    assert composed.fingerprint == authored_fingerprint
    assert composed.manifest == authored_manifest


def test_structural_resolution_receives_recipe_expansion_output(
    tmp_path: Path,
) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(
        "root: /prepared\n"
        "pipeline:\n"
        "  _recipe_: structural-action\n"
        "  manifest_path: ${root}/manifest.json\n",
        encoding="utf-8",
    )
    catalog = RecipeCatalog()

    def structural_action(manifest_path: str) -> dict[str, object]:
        return {
            "manifest_path": {
                "_resolve_": {
                    "resolver": "example.runtime",
                    "version": 1,
                    "declared_path": manifest_path,
                }
            }
        }

    catalog.register("structural-action", structural_action)
    composed = compose_config(base, recipe_catalog=catalog)
    action = composed.resolved["pipeline"]

    result = resolve_structural(
        action,
        resolvers={
            "example.runtime": StructuralResolverDefinition(
                version=1,
                handler=lambda request: request.arguments["declared_path"],
            )
        },
    )

    assert result.value == {"manifest_path": "/prepared/manifest.json"}
    assert composed.recipe_manifest[0]["name"] == "structural-action"


def test_concurrent_compositions_isolate_environments_and_preserve_process_state(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text("value: ${oc.env:VALUE}\nwork: {_recipe_: rendezvous}\n", encoding="utf-8")
    rendezvous = Barrier(2, timeout=10)
    catalog = RecipeCatalog()
    observed_environments = []

    def pause() -> dict[str, str]:
        observed_environments.append(dict(os.environ))
        rendezvous.wait()
        return {"copy": "${oc.env:VALUE}"}

    catalog.register("rendezvous", pause)
    before = dict(os.environ)
    global_resolver = OmegaConf._get_resolver("oc.env")

    def compose(value: str) -> dict:
        return compose_config(base, recipe_catalog=catalog, environment={"VALUE": value}).resolved

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(compose, ["agent-a", "agent-b"]))
    assert results == [
        {"value": "agent-a", "work": {"copy": "agent-a"}},
        {"value": "agent-b", "work": {"copy": "agent-b"}},
    ]
    assert observed_environments == [before, before]
    assert dict(os.environ) == before
    assert OmegaConf._get_resolver("oc.env") is global_resolver


@pytest.mark.parametrize("explicit", [False, True])
def test_composition_snapshots_environment_before_recipe_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, explicit: bool,
) -> None:
    base = tmp_path / "base.yaml"
    base.write_text("value: ${oc.env:VALUE}\nwork: {_recipe_: mutate}\n", encoding="utf-8")
    environment = {"VALUE": "before"}
    monkeypatch.setenv("VALUE", "before")
    catalog = RecipeCatalog()

    def mutate() -> dict[str, str]:
        environment["VALUE"] = "after"
        monkeypatch.setenv("VALUE", "after")
        return {"copy": "${oc.env:VALUE}"}

    catalog.register("mutate", mutate)
    composed = compose_config(
        base, recipe_catalog=catalog,
        environment=MappingProxyType(environment) if explicit else None,
    )
    assert composed.resolved == {"value": "before", "work": {"copy": "before"}}
    assert os.environ["VALUE"] == "after"


@pytest.mark.parametrize("entrypoint", [
    "compose_config", "inspect_config_composition", "compose_config_with_catalog",
    "compose_config_from_args", "inspect_config_args", "compose_config_from_argv", "inspect_config_from_argv",
    "compose_args", "inspect_args",
])
def test_public_composition_wrappers_forward_environment(tmp_path: Path, entrypoint: str) -> None:
    base = tmp_path / "base.yaml"
    base.write_text("value: ${oc.env:VALUE}\n", encoding="utf-8")
    catalog = RecipeCatalog()
    environment = {"VALUE": "explicit"}
    direct = {
        "compose_config": compose_config,
        "inspect_config_composition": inspect_config_composition,
        "compose_config_with_catalog": compose_config_with_catalog,
    }
    args = {"compose_config_from_args": compose_config_from_args, "inspect_config_args": inspect_config_args}
    argv = {"compose_config_from_argv": compose_config_from_argv, "inspect_config_from_argv": inspect_config_from_argv}
    if entrypoint in direct:
        result = direct[entrypoint](base, recipe_catalog=catalog, environment=environment)
    elif entrypoint in args:
        result = args[entrypoint](base, environment=environment)
    elif entrypoint in argv:
        result = argv[entrypoint]([str(base)], environment=environment)
    else:
        result = getattr(ConfigEntrypoint(base_config_path=base), entrypoint)(environment=environment)
    if hasattr(result, "composed_config"):
        result = result.composed_config
    elif hasattr(result, "inspection"):
        result = result.inspection
    assert result.resolved == {"value": "explicit"}


@pytest.mark.parametrize("explicit", [False, True])
def test_entrypoint_snapshots_environment_before_base_resolver(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, explicit: bool,
) -> None:
    from weave.api import ConfigBaseResolution

    base = tmp_path / "base.yaml"
    base.write_text("value: ${oc.env:VALUE}\n", encoding="utf-8")
    environment = {"VALUE": "before"}
    monkeypatch.setenv("VALUE", "before")

    def resolver(request):
        environment["VALUE"] = "after"
        monkeypatch.setenv("VALUE", "after")
        return ConfigBaseResolution(base)

    result = ConfigEntrypoint(base_resolver=resolver).compose_args(environment=environment if explicit else None)
    assert result.composed_config.resolved == {"value": "before"}
