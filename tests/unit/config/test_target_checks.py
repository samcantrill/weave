"""Unit tests for config target check helpers."""

from __future__ import annotations

import pytest

from weave import check_config_targets
from weave.errors import ConfigStructuralResolutionError


pytestmark = pytest.mark.unit

target_events: list[str] = []
TARGET_PATH = f"{__name__}:record_target"


def record_target(*, tag: str, child: object | None = None) -> dict[str, object]:
    target_events.append(tag)
    return {"tag": tag, "child": child}


def test_check_config_targets_constructs_nested_target_tree_once() -> None:
    target_events.clear()

    result = check_config_targets(
        {
            "service": {
                "_target_": TARGET_PATH,
                "tag": "parent",
                "child": {
                    "_target_": TARGET_PATH,
                    "tag": "child",
                },
            }
        }
    )

    assert result.target_count == 2
    assert result.checked_paths == ("$.service", "$.service.child")
    assert target_events == ["child", "parent"]


def test_check_config_targets_skips_owner_paths_but_checks_nested_targets() -> None:
    target_events.clear()

    result = check_config_targets(
        {
            "factory": {
                "_target_": TARGET_PATH,
                "tag": "owner",
                "child": {
                    "_target_": TARGET_PATH,
                    "tag": "child",
                },
            }
        },
        skip_paths=("$.factory",),
    )

    assert result.target_count == 1
    assert result.checked_paths == ("$.factory.child",)
    assert target_events == ["child"]


def test_check_config_targets_preflights_whole_input_before_construction() -> None:
    target_events.clear()

    with pytest.raises(ConfigStructuralResolutionError) as exc:
        check_config_targets(
            {
                "first": {
                    "_target_": TARGET_PATH,
                    "tag": "must-not-run",
                },
                "later": {
                    "_resolve_": {
                        "resolver": "example.runtime",
                        "version": 1,
                    }
                },
            }
        )

    assert target_events == []
    assert exc.value.context is not None
    assert exc.value.context.code == "unresolved_structural_directive"
    assert exc.value.context.config_path == "$.later"
