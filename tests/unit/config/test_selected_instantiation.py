"""Unit tests for selected object instantiation coordination."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import pytest

from weave import ConfigEntrypoint
from weave.errors import ConfigValidationError


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def assert_selected_error(
    exc: pytest.ExceptionInfo[ConfigValidationError], code: str
) -> None:
    context = exc.value.context
    assert context is not None
    assert context.code == code
    assert context.source_kind == "config_entrypoint"
    assert context.source_path == "<config-entrypoint>"
    assert context.directive == "selected_instantiation"


def test_config_entrypoint_rejects_invalid_selected_objects() -> None:
    with pytest.raises(ConfigValidationError) as raw_string:
        ConfigEntrypoint(
            base_config_path="base.yaml",
            selected_objects="model",  # type: ignore[arg-type]
        )
    assert_selected_error(raw_string, "invalid_selected_objects")

    with pytest.raises(ConfigValidationError) as unordered_paths:
        ConfigEntrypoint(
            base_config_path="base.yaml",
            selected_objects=cast(Sequence[str], {"model"}),
        )
    assert_selected_error(unordered_paths, "invalid_selected_objects")

    with pytest.raises(ConfigValidationError) as empty_key:
        ConfigEntrypoint(base_config_path="base.yaml", selected_objects={"": "model"})
    assert_selected_error(empty_key, "invalid_selected_object_key")

    with pytest.raises(ConfigValidationError) as empty_segment:
        ConfigEntrypoint(base_config_path="base.yaml", selected_objects=["model..name"])
    assert_selected_error(empty_segment, "invalid_selected_object_path")

    with pytest.raises(ConfigValidationError) as non_string_path:
        ConfigEntrypoint(
            base_config_path="base.yaml", selected_objects=cast(Sequence[str], [1])
        )
    assert_selected_error(non_string_path, "invalid_selected_object_path")

    with pytest.raises(ConfigValidationError) as duplicate_key:
        ConfigEntrypoint(
            base_config_path="base.yaml", selected_objects=["model", "model"]
        )
    assert_selected_error(duplicate_key, "duplicate_selected_object_key")


def test_config_entrypoint_rejects_invalid_selected_runtime() -> None:
    with pytest.raises(ConfigValidationError) as exc:
        ConfigEntrypoint(
            base_config_path="base.yaml",
            runtime=cast(Mapping[str, object], "not-a-mapping"),
        )

    assert_selected_error(exc, "invalid_selected_runtime")
    assert exc.value.context is not None
    assert exc.value.context.details == {"actual_type": "str"}


def test_selected_object_missing_path_has_structured_context(tmp_path: Path) -> None:
    base = _write(tmp_path / "base.yaml", "model:\n  name: base\n")
    entrypoint = ConfigEntrypoint(
        base_config_path=base, selected_objects={"chosen": "model.missing"}
    )

    with pytest.raises(ConfigValidationError) as exc:
        entrypoint.compose_args()

    assert_selected_error(exc, "missing_selected_object_path")
    assert exc.value.context is not None
    assert exc.value.context.config_path == "$.model.missing"
    assert exc.value.context.details == {
        "key": "chosen",
        "path": "model.missing",
        "missing_segment": "missing",
        "traversed_path": ["model"],
    }


def test_selected_object_non_mapping_parent_has_structured_context(
    tmp_path: Path,
) -> None:
    base = _write(tmp_path / "base.yaml", "leaf: value\n")
    entrypoint = ConfigEntrypoint(
        base_config_path=base, selected_objects=["leaf.child"]
    )

    with pytest.raises(ConfigValidationError) as exc:
        entrypoint.compose_args()

    assert_selected_error(exc, "non_mapping_selected_object_parent")
    assert exc.value.context is not None
    assert exc.value.context.config_path == "$.leaf"
    assert exc.value.context.details == {
        "key": "leaf.child",
        "path": "leaf.child",
        "traversed_path": ["leaf"],
    }


def test_inspect_args_does_not_instantiate_selected_objects(tmp_path: Path) -> None:
    base = _write(
        tmp_path / "base.yaml",
        "service:\n  _target_: tests.support.config_samples:NON_CALLABLE_TARGET\n",
    )
    entrypoint = ConfigEntrypoint(
        base_config_path=base, selected_objects={"service": "service"}
    )

    result = entrypoint.inspect_args()

    assert not hasattr(result, "objects")
    assert result.inspection.resolved["service"] == {
        "_target_": "tests.support.config_samples:NON_CALLABLE_TARGET"
    }
