"""Order-preserving plain configuration transport and identity.

Protocol envelopes may sort their keys. Mapping entries and sequence members
are represented by arrays so nested authored order survives those envelopes.
Decode only in the consuming process; re-encode before another transport.
"""

from __future__ import annotations

from typing import cast

from .digests import hash_mapping
from .errors import DeserializationError
from .plain import PlainData, ensure_plain_data

ORDERED_CONFIG_SCHEMA = "weave.ordered-config.v1"


def encode_ordered_config(value: object) -> dict[str, PlainData]:
    """Encode finite plain configuration, retaining mapping order and list duplicates.

    String-keyed mappings, lists/tuples and finite JSON scalars are supported.
    Tuples normalize to lists. The returned versioned envelope is ordinary plain
    data and is safe to pass through canonical key-sorting JSON serializers.
    """
    return {"schema": ORDERED_CONFIG_SCHEMA, "value": _encode(ensure_plain_data(value))}


def decode_ordered_config(value: object) -> PlainData:
    """Validate an ordered envelope and restore dictionaries in authored order.

    Unsupported versions, malformed nodes, duplicate/non-string mapping keys and
    non-finite/non-plain values are refused. No order is inferred from legacy
    plain mappings; callers must select the appropriate versioned wire contract.
    """
    plain = ensure_plain_data(value)
    if not isinstance(plain, dict) or set(plain) != {"schema", "value"}:
        raise DeserializationError("Ordered configuration requires schema and value")
    if plain["schema"] != ORDERED_CONFIG_SCHEMA:
        raise DeserializationError("Unsupported ordered configuration schema")
    return _decode(plain["value"], "$")


def ordered_config_fingerprint(value: object) -> str:
    """Hash configuration with nested mapping and sequence order as semantic data."""
    return hash_mapping(encode_ordered_config(value))


def _encode(value: PlainData) -> dict[str, PlainData]:
    if isinstance(value, dict):
        return {
            "kind": "mapping",
            "items": [[key, _encode(child)] for key, child in value.items()],
        }
    if isinstance(value, list):
        return {"kind": "sequence", "items": [_encode(child) for child in value]}
    return {"kind": "scalar", "value": value}


def _decode(node: PlainData, path: str) -> PlainData:
    if not isinstance(node, dict):
        raise DeserializationError(
            f"Ordered configuration node must be a mapping at {path}"
        )
    kind = node.get("kind")
    if kind == "scalar" and set(node) == {"kind", "value"}:
        value = node["value"]
        if isinstance(value, (dict, list)):
            raise DeserializationError(f"Ordered scalar contains a container at {path}")
        return value
    if kind not in ("mapping", "sequence") or set(node) != {"kind", "items"}:
        raise DeserializationError(f"Invalid ordered configuration node at {path}")
    items = node["items"]
    if not isinstance(items, list):
        raise DeserializationError(
            f"Ordered configuration items must be a list at {path}"
        )
    if kind == "sequence":
        return [_decode(child, f"{path}[{index}]") for index, child in enumerate(items)]
    result: dict[str, PlainData] = {}
    for index, pair in enumerate(items):
        if not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str):
            raise DeserializationError(
                f"Ordered mapping requires key/value pairs at {path}[{index}]"
            )
        key = cast(str, pair[0])
        if key in result:
            raise DeserializationError(
                f"Duplicate ordered mapping key at {path}[{key!r}]"
            )
        result[key] = _decode(pair[1], f"{path}[{key!r}]")
    return result


__all__ = [
    "ORDERED_CONFIG_SCHEMA",
    "encode_ordered_config",
    "decode_ordered_config",
    "ordered_config_fingerprint",
]
