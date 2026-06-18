"""Unit tests for config entrypoint base resolution records."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

from weave.api import ConfigBaseRequest, ConfigBaseResolution, ConfigEntrypoint
from weave.errors import ConfigValidationError


def assert_entrypoint_error(exc: pytest.ExceptionInfo[ConfigValidationError], code: str) -> None:
    context = exc.value.context
    assert context is not None
    assert context.code == code
    assert context.source_kind == "config_entrypoint"
    assert context.source_path == "<config-entrypoint>"
    assert context.directive == "base_resolution"


def test_config_base_resolution_normalizes_path_and_details(tmp_path: Path) -> None:
    base = tmp_path / "configs" / "base.yaml"

    resolution = ConfigBaseResolution(
        base_config_path=base,
        details={"strategy": "profile", "profile": "dev", "orders": [1, 2]},
    )

    assert resolution.base_config_path == str(base)
    assert resolution.details == {"strategy": "profile", "profile": "dev", "orders": [1, 2]}
    assert resolution.to_dict() == {
        "base_config_path": str(base),
        "details": {"strategy": "profile", "profile": "dev", "orders": [1, 2]},
    }


def test_config_base_resolution_rejects_empty_path() -> None:
    with pytest.raises(ConfigValidationError, match="base_config_path must be non-empty"):
        ConfigBaseResolution(base_config_path="")


def test_config_base_resolution_rejects_non_plain_details() -> None:
    with pytest.raises(ConfigValidationError, match="details must be plain data"):
        ConfigBaseResolution(base_config_path="base.yaml", details={"bad": {"not-plain"}})  # type: ignore[dict-item]


def test_config_entrypoint_requires_exactly_one_base_strategy() -> None:
    with pytest.raises(ConfigValidationError) as missing:
        ConfigEntrypoint()
    assert_entrypoint_error(missing, "missing_base_strategy")
    assert missing.value.context is not None
    assert missing.value.context.details == {
        "has_base_config_path": False,
        "has_base_resolver": False,
    }

    def resolver(_: ConfigBaseRequest) -> ConfigBaseResolution:
        return ConfigBaseResolution(base_config_path="base.yaml")

    with pytest.raises(ConfigValidationError) as conflicting:
        ConfigEntrypoint(base_config_path="base.yaml", base_resolver=resolver)
    assert_entrypoint_error(conflicting, "conflicting_base_strategies")
    assert conflicting.value.context is not None
    assert conflicting.value.context.details == {
        "has_base_config_path": True,
        "has_base_resolver": True,
    }


def test_config_entrypoint_rejects_non_callable_resolver() -> None:
    resolver = cast(Callable[[ConfigBaseRequest], ConfigBaseResolution], object())

    with pytest.raises(ConfigValidationError) as exc:
        ConfigEntrypoint(base_resolver=resolver)

    assert_entrypoint_error(exc, "invalid_base_resolver")
    assert exc.value.context is not None
    assert exc.value.context.details == {"actual_type": "object"}


def test_config_entrypoint_rejects_invalid_resolver_return() -> None:
    def resolver(_: ConfigBaseRequest) -> ConfigBaseResolution:
        return cast(ConfigBaseResolution, "base.yaml")

    entrypoint = ConfigEntrypoint(base_resolver=resolver)

    with pytest.raises(ConfigValidationError) as exc:
        entrypoint.inspect_args()

    assert_entrypoint_error(exc, "invalid_base_resolution")
    assert exc.value.context is not None
    assert exc.value.context.details == {"actual_type": "str"}


def test_config_entrypoint_passes_opaque_base_context_to_resolver() -> None:
    context = object()
    seen: list[object | None] = []

    def resolver(request: ConfigBaseRequest) -> ConfigBaseResolution:
        seen.append(request.base_context)
        return ConfigBaseResolution(base_config_path="base.yaml", details={"strategy": "unit"})

    entrypoint = ConfigEntrypoint(base_resolver=resolver, base_context=context)
    base_path, base_details = entrypoint._resolve_base()

    assert seen == [context]
    assert base_path == "base.yaml"
    assert base_details == ({"strategy": "unit"},)
