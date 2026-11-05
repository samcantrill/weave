"""Configuration order is data, including across canonical protocol JSON."""

import json
import math

import pytest

from weave import (
    decode_ordered_config,
    encode_ordered_config,
    ordered_config_fingerprint,
)
from weave.errors import DeserializationError, PlainDataError
from weave.json import stable_json_dumps


def test_nested_mapping_order_and_duplicate_sequences_survive_canonical_transport():
    config = {
        "parts": {
            "reconstruction": {"z": [3, 1, 3], "a": None},
            "detrending": {"operations": ["z", "a", "z"]},
        },
        "empty_mapping": {},
        "empty_sequence": [],
        "scalars": [True, False, 4, -2, 0.25, "value"],
    }
    encoded = encode_ordered_config(config)
    wire = stable_json_dumps(encoded)
    restored = decode_ordered_config(json.loads(wire))
    assert restored == config
    assert list(restored) == list(config)
    assert list(restored["parts"]) == ["reconstruction", "detrending"]
    assert list(restored["parts"]["reconstruction"]) == ["z", "a"]
    assert encode_ordered_config(restored) == encoded
    assert ordered_config_fingerprint(restored) == ordered_config_fingerprint(config)
    changed = dict(config)
    changed["parts"] = dict(reversed(list(config["parts"].items())))
    assert changed == config  # Ordinary dict equality does not prove equal order.
    assert ordered_config_fingerprint(changed) != ordered_config_fingerprint(config)
    changed["parts"] = dict(config["parts"])
    changed["parts"]["detrending"] = {"operations": ["a", "z", "z"]}
    assert ordered_config_fingerprint(changed) != ordered_config_fingerprint(config)


def test_tuple_normalizes_to_sequence_and_user_keys_do_not_collide_with_tags():
    config = {"schema": "weave.ordered-config.v1", "kind": "mapping", "items": (1, 1)}
    assert decode_ordered_config(encode_ordered_config(config)) == {
        **config,
        "items": [1, 1],
    }


@pytest.mark.parametrize(
    "value", [float("nan"), math.inf, -math.inf, {1: "bad"}, {"s": {1, 2}}]
)
def test_encoding_refuses_nonfinite_or_nonplain_config(value):
    with pytest.raises(PlainDataError):
        encode_ordered_config(value)


@pytest.mark.parametrize(
    "node",
    [
        None,
        {"kind": "unknown", "items": []},
        {"kind": "scalar", "value": {}},
        {"kind": "scalar", "value": []},
        {"kind": "scalar", "value": 1, "extra": True},
        {"kind": "sequence", "items": {}},
        {"kind": "mapping", "items": [[1, {"kind": "scalar", "value": 0}]]},
        {"kind": "mapping", "items": [["a"]]},
        {
            "kind": "mapping",
            "items": [
                ["a", {"kind": "scalar", "value": 0}],
                ["a", {"kind": "scalar", "value": 1}],
            ],
        },
    ],
)
def test_decode_refuses_malformed_nodes(node):
    with pytest.raises(DeserializationError):
        decode_ordered_config({"schema": "weave.ordered-config.v1", "value": node})


@pytest.mark.parametrize(
    "payload", [{}, {"schema": "weave.ordered-config.v0", "value": None}]
)
def test_decode_never_infers_order_from_legacy_or_unknown_payloads(payload):
    with pytest.raises(DeserializationError):
        decode_ordered_config(payload)


def test_composition_overlays_references_and_replacement_preserve_authored_order(
    tmp_path,
):
    from weave import compose_config

    (tmp_path / "fragment.yaml").write_text(
        "steps:\n  z: 1\n  a: 2\nvalues: [3, 1, 3]\n"
    )
    base = tmp_path / "base.yaml"
    base.write_text("_include_: ./fragment.yaml\nselected: ${steps}\n")
    overlay = tmp_path / "overlay.yaml"
    overlay.write_text("steps:\n  z: 4\n  c: 5\n  b: 6\nvalues: [9, 2, 9]\n")
    resolved = compose_config(base, overlays=(overlay,)).resolved
    restored = decode_ordered_config(
        json.loads(stable_json_dumps(encode_ordered_config(resolved)))
    )
    assert list(restored["steps"]) == ["z", "a", "c", "b"]
    assert list(restored["selected"]) == ["z", "a", "c", "b"]
    assert restored["steps"]["z"] == 4
    assert restored["values"] == [9, 2, 9]
    replacement = tmp_path / "replace.yaml"
    replacement.write_text("steps:\n  _replace_: true\n  b: 7\n  a: 8\n")
    replaced = compose_config(base, overlays=(overlay, replacement)).resolved
    assert list(replaced["steps"]) == ["b", "a"]
    assert list(replaced["selected"]) == ["b", "a"]


def test_artifact_fingerprint_distinguishes_mapping_order_with_identical_source_facts():
    from weave.fingerprints import (
        build_artifact_safe_config_fingerprint_record,
        compare_config_artifact_fingerprints,
    )
    from weave.artifacts import ConfigFingerprintRecord

    def record(value):
        return build_artifact_safe_config_fingerprint_record(
            unresolved=value,
            redacted=value,
            source_artifacts=(),
            include_sites=(),
            include_overrides=(),
            ordinary_overrides=(),
            recipe_manifest=(),
            resolver_records=(),
            redaction_policy={},
        )

    left = record({"steps": {"z": 1, "a": 2}})
    right = record({"steps": {"a": 2, "z": 1}})
    assert left.digest != right.digest
    retained = ConfigFingerprintRecord.from_dict(
        json.loads(stable_json_dumps(left.to_dict()))
    )
    assert compare_config_artifact_fingerprints(left, retained).status == "match"
    legacy = left.to_dict()
    legacy["metadata"]["fingerprint_policy"] = "artifact_safe_authored_composition_v1"
    legacy["metadata"]["payload_schema_version"] = 1
    assert (
        compare_config_artifact_fingerprints(left, legacy).status
        == "incompatible_policy"
    )
