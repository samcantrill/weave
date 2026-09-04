# Structural Resolution

This example keeps runtime authority lookup separate from authored composition:

1. compose `config.yaml` and fix its authored fingerprint;
2. resolve one `_resolve_` envelope with a namespaced implementation supplied
   only for that call;
3. inspect ordered, redacted records that omit the actual runtime path; and
4. explicitly instantiate the remaining `_target_` mapping.

Run from the repository root:

```sh
uv run python examples/structural-resolution/resolve_action.py
```
