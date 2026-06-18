"""Integration tests for selected object instantiation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from weave import ConfigEntrypoint
from tests.support.config_samples import (
    RuntimePlaceholder,
    construction_event_log,
    reset_instantiate_probe_state,
)


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_entrypoint_instantiates_selected_targets_and_plain_values(
    tmp_path: Path,
) -> None:
    base = _write(
        tmp_path / "base.yaml",
        "service:\n"
        "  _target_: tests.support.config_samples:RuntimePlaceholder\n"
        "  _inject_:\n"
        "    value: service_value\n"
        "plain:\n"
        "  value: 7\n",
    )
    runtime_value = object()

    result = ConfigEntrypoint(
        base_config_path=base,
        selected_objects={"service_obj": "service", "plain_value": "plain.value"},
        runtime={"service_value": runtime_value},
    ).compose_args()

    assert set(result.objects) == {"service_obj", "plain_value"}
    service = result.objects["service_obj"]
    assert isinstance(service, RuntimePlaceholder)
    assert service.value is runtime_value
    assert result.objects["plain_value"] == 7
    assert result.selected_objects == (
        {"key": "service_obj", "path": "service"},
        {"key": "plain_value", "path": "plain.value"},
    )

    payload = result.to_dict()
    assert "objects" not in payload
    assert payload["selected_objects"] == [
        {"key": "service_obj", "path": "service"},
        {"key": "plain_value", "path": "plain.value"},
    ]
    json.dumps(payload, sort_keys=True)


def test_entrypoint_sequence_selectors_key_objects_by_dot_path(tmp_path: Path) -> None:
    base = _write(tmp_path / "base.yaml", "plain:\n  value: selected\n")

    result = ConfigEntrypoint(
        base_config_path=base, selected_objects=["plain.value"]
    ).compose_args()

    assert result.objects == {"plain.value": "selected"}
    assert result.selected_objects == ({"key": "plain.value", "path": "plain.value"},)
    assert result.to_dict()["selected_objects"] == [
        {"key": "plain.value", "path": "plain.value"}
    ]


def test_entrypoint_is_inert_without_selected_objects(tmp_path: Path) -> None:
    reset_instantiate_probe_state()
    base = _write(
        tmp_path / "base.yaml",
        "probe:\n"
        "  _target_: tests.support.config_samples:log_and_return\n"
        "  tag: selected\n"
        "  value: payload\n",
    )

    result = ConfigEntrypoint(base_config_path=base).compose_args()

    assert result.objects == {}
    assert result.selected_objects == ()
    assert result.to_dict()["selected_objects"] == []
    assert construction_event_log == []
    resolved_probe = cast(dict[str, Any], result.composed_config.resolved["probe"])
    assert resolved_probe["_target_"] == "tests.support.config_samples:log_and_return"
