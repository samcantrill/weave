"""Unit contracts for call-scoped structural resolution."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import pytest

from tests.support.config_samples import (
    construction_event_log,
    reset_instantiate_probe_state,
)
from weave import (
    StructuralResolutionRecord,
    StructuralResolutionRequest,
    StructuralResolverDefinition,
    StructuralResolverRejected,
    instantiate,
    resolve_structural,
)
from weave.errors import ConfigStructuralResolutionError
from weave.redaction import REDACTION_MARKER


def _directive(
    resolver: str = "example.runtime",
    *,
    version: int = 1,
    **arguments: object,
) -> dict[str, object]:
    return {
        "_resolve_": {
            "resolver": resolver,
            "version": version,
            **arguments,
        }
    }


def _definition(
    handler: Any,
    *,
    version: int = 1,
) -> dict[str, StructuralResolverDefinition]:
    return {
        "example.runtime": StructuralResolverDefinition(
            version=version,
            handler=handler,
        )
    }


def _assert_structural_error(
    exc: pytest.ExceptionInfo[ConfigStructuralResolutionError],
    code: str,
) -> None:
    context = exc.value.context
    assert context is not None
    assert context.code == code
    assert context.source_kind == "structural_resolution"
    assert context.source_path == "<structural-resolution>"
    assert context.directive == "_resolve_"


def test_resolve_structural_is_ordered_immutable_and_preserves_declarations() -> None:
    calls: list[tuple[str, object]] = []

    def handler(request: StructuralResolutionRequest) -> object:
        value = request.arguments["value"]
        calls.append((request.config_path, value))
        if isinstance(value, Mapping):
            value = dict(value)
        return {"resolved": value}

    nested = _directive(value="inner")
    source = {
        "z": _directive(value="z"),
        "outer": _directive(value=nested),
        "a": _directive(value="a"),
    }
    expected_source = {
        "z": _directive(value="z"),
        "outer": _directive(value=_directive(value="inner")),
        "a": _directive(value="a"),
    }

    result = resolve_structural(source, resolvers=_definition(handler))

    assert source == expected_source
    assert calls == [
        ("$.a", "a"),
        ("$.outer._resolve_.value", "inner"),
        ("$.outer", {"resolved": "inner"}),
        ("$.z", "z"),
    ]
    assert result.value == {
        "a": {"resolved": "a"},
        "outer": {"resolved": {"resolved": "inner"}},
        "z": {"resolved": "z"},
    }
    assert [record.order for record in result.records] == [0, 1, 2, 3]
    assert [record.config_path for record in result.records] == [
        "$.a",
        "$.outer._resolve_.value",
        "$.outer",
        "$.z",
    ]
    parent_record = result.records[2].to_dict()
    assert parent_record["arguments"] == {"value": nested}
    assert "resolved" not in str(parent_record["arguments"])


def test_request_arguments_are_deeply_immutable() -> None:
    def handler(request: StructuralResolutionRequest) -> object:
        with pytest.raises(TypeError):
            request.arguments["new"] = "value"  # type: ignore[index]
        nested = cast(Mapping[str, object], request.arguments["nested"])
        with pytest.raises(TypeError):
            nested["value"] = "changed"  # type: ignore[index]
        items = cast(tuple[object, ...], request.arguments["items"])
        assert items == (1, 2)
        return "done"

    result = resolve_structural(
        _directive(nested={"value": "original"}, items=[1, 2]),
        resolvers=_definition(handler),
    )

    assert result.value == "done"


def test_resolution_detaches_input_output_and_repeated_aliases() -> None:
    shared_input = {"items": [1]}
    shared_output = ["runtime"]
    source = {
        "left": shared_input,
        "right": shared_input,
        "runtime": _directive(),
    }

    result = resolve_structural(
        source,
        resolvers=_definition(lambda _request: {"left": shared_output, "right": shared_output}),
    )

    value = cast(dict[str, Any], result.value)
    assert value["left"] is not value["right"]
    runtime = cast(dict[str, list[str]], value["runtime"])
    assert runtime["left"] is not runtime["right"]
    cast(dict[str, list[int]], value["left"])["items"].append(2)
    assert cast(dict[str, list[int]], value["right"])["items"] == [1]
    assert shared_input == {"items": [1]}
    assert shared_output == ["runtime"]


def test_all_directives_are_validated_before_any_handler_runs() -> None:
    calls: list[str] = []

    def handler(request: StructuralResolutionRequest) -> str:
        calls.append(request.config_path)
        return "resolved"

    source = {
        "a": _directive(),
        "z": _directive("missing.runtime"),
    }

    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(source, resolvers=_definition(handler))

    _assert_structural_error(exc, "unknown_structural_resolver")
    assert calls == []


def test_resolver_implementations_are_isolated_to_one_call() -> None:
    source = _directive(value="ok")
    result = resolve_structural(
        source,
        resolvers=_definition(lambda request: request.arguments["value"]),
    )
    assert result.value == "ok"

    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(source, resolvers={})

    _assert_structural_error(exc, "unknown_structural_resolver")


def test_resolver_version_must_match_exactly() -> None:
    calls: list[str] = []

    def handler(request: StructuralResolutionRequest) -> None:
        calls.append(request.config_path)

    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(
            {
                "a": _directive(),
                "z": _directive(version=2),
            },
            resolvers=_definition(handler, version=1),
        )

    _assert_structural_error(exc, "structural_resolver_version_mismatch")
    assert exc.value.context is not None
    assert exc.value.context.expected == 1
    assert exc.value.context.actual == 2
    assert calls == []


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ({"_resolve_": "bad"}, "invalid_structural_directive"),
        (
            {"_resolve_": {"resolver": "example.runtime", "version": 1}, "x": 1},
            "ambiguous_structural_directive",
        ),
        (
            {"_resolve_": {"resolver": "not_namespaced", "version": 1}},
            "invalid_structural_resolver_name",
        ),
        (
            {"_resolve_": {"resolver": "example.runtime", "version": True}},
            "invalid_structural_resolver_version",
        ),
    ],
)
def test_invalid_directive_shapes_are_explicit(
    source: object,
    code: str,
) -> None:
    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(
            source,
            resolvers=_definition(lambda _request: "unused"),
        )

    _assert_structural_error(exc, code)


def test_weave_resolver_namespace_is_reserved() -> None:
    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(
            _directive("weave.runtime"),
            resolvers={
                "weave.runtime": StructuralResolverDefinition(
                    version=1,
                    handler=lambda _request: None,
                )
            },
        )

    _assert_structural_error(exc, "reserved_structural_resolver_name")


@pytest.mark.parametrize("output", [Path("runtime.txt"), float("nan"), object()])
def test_resolver_outputs_must_be_finite_plain_data(output: object) -> None:
    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(
            _directive(),
            resolvers=_definition(lambda _request: output),
        )

    _assert_structural_error(exc, "structural_resolver_output_not_plain_data")


def test_cyclic_input_and_output_are_rejected_explicitly() -> None:
    cyclic_input: dict[str, object] = {}
    cyclic_input["self"] = cyclic_input
    with pytest.raises(ConfigStructuralResolutionError) as input_exc:
        resolve_structural(cyclic_input, resolvers={})
    _assert_structural_error(input_exc, "structural_resolution_cycle")
    assert input_exc.value.context is not None
    assert input_exc.value.context.details["phase"] == "input"

    cyclic_output: list[object] = []
    cyclic_output.append(cyclic_output)
    with pytest.raises(ConfigStructuralResolutionError) as output_exc:
        resolve_structural(
            _directive(),
            resolvers=_definition(lambda _request: cyclic_output),
        )
    _assert_structural_error(output_exc, "structural_resolution_cycle")
    assert output_exc.value.context is not None
    assert output_exc.value.context.details["phase"] == "resolver_output"


def test_resolver_may_not_generate_another_directive() -> None:
    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(
            _directive(),
            resolvers=_definition(lambda _request: _directive(value="dynamic")),
        )

    _assert_structural_error(exc, "unresolved_structural_output")
    assert exc.value.context is not None
    assert exc.value.context.config_path == "$"


def test_generic_handler_failure_does_not_serialize_exception_text() -> None:
    def fail(_request: StructuralResolutionRequest) -> object:
        raise RuntimeError("raw-runtime-secret")

    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(_directive(), resolvers=_definition(fail))

    _assert_structural_error(exc, "structural_resolver_failed")
    payload = str(exc.value.to_dict())
    assert "raw-runtime-secret" not in payload
    assert "RuntimeError" in payload
    assert exc.value.__cause__ is None
    assert exc.value.__context__ is None


def test_explicit_rejection_details_and_records_use_secret_redaction() -> None:
    def reject(_request: StructuralResolutionRequest) -> object:
        raise StructuralResolverRejected(
            "authority_missing",
            details={"api_token": "raw-token", "authority": "dataset"},
        )

    with pytest.raises(ConfigStructuralResolutionError) as exc:
        resolve_structural(_directive(), resolvers=_definition(reject))

    _assert_structural_error(exc, "structural_resolver_rejected")
    assert exc.value.context is not None
    assert exc.value.context.details["rejection_details"] == {
        "api_token": REDACTION_MARKER,
        "authority": "dataset",
    }
    assert exc.value.__cause__ is None
    assert exc.value.__context__ is None

    result = resolve_structural(
        _directive(api_token="raw-token", label="safe"),
        resolvers=_definition(lambda _request: "runtime-secret-value"),
    )
    record = result.records[0].to_dict()
    assert record["arguments"] == {
        "api_token": REDACTION_MARKER,
        "label": "safe",
    }
    assert "runtime-secret-value" not in repr(result)
    assert "runtime-secret-value" not in repr(result.records)
    json.dumps(record, sort_keys=True)

    secret_path_result = resolve_structural(
        {"api_token": _directive(label="safe")},
        resolvers=_definition(lambda _request: "usable-secret"),
    )
    assert secret_path_result.records[0].to_dict()["arguments"] == REDACTION_MARKER


def test_record_schema_round_trips_as_plain_data() -> None:
    result = resolve_structural(
        _directive(value=3),
        resolvers=_definition(lambda request: request.arguments["value"]),
    )
    payload = result.records[0].to_dict()

    rebuilt = StructuralResolutionRecord.from_dict(payload)

    assert rebuilt == result.records[0]
    assert rebuilt.to_dict() == payload


def test_resolver_returned_targets_remain_inert_until_explicit_instantiation() -> None:
    reset_instantiate_probe_state()
    result = resolve_structural(
        _directive(),
        resolvers=_definition(
            lambda _request: {
                "_target_": "tests.support.config_samples:log_and_return",
                "tag": "resolved-target",
                "value": "payload",
            }
        ),
    )

    assert construction_event_log == []
    assert instantiate(result.value) == "payload"
    assert construction_event_log == ["resolved-target"]
