# Configuration Composition

`weave` composes trusted project configuration into deterministic plain data and
auditable records.

## Supported Behavior

- YAML loading with duplicate-key, recursive-alias, unsupported-directive, and
  root-mapping checks.
- Base config plus overlay files.
- Recursive merge semantics with `_replace_: true` for intentional mapping
  replacement.
- `_include_` directives for local and `file://` config fragments, with cycle
  diagnostics and path-aware source context.
- Strict dot-path overrides where `path=value` updates an existing path and
  `+path=value` adds a missing path.
- OmegaConf interpolation with a narrow resolver policy.
- Recipe expansion through `RecipeCatalog`, recipe manifests, and trusted recipe
  plugin loading.
- Secret redaction, provenance, source artifact records, raw source snapshot
  records, composition manifests, and config fingerprints.
- Trusted `_target_` object graph construction via `instantiate(...)`.

## Public API

```python
from weave import (
    ConfigError,
    Recipe,
    RecipeCatalog,
    compose_config,
    compose_config_from_argv,
    compose_config_with_catalog,
    inspect_config_composition,
    instantiate,
    register_recipe,
)
```

Detailed argv result and inspection types are available from `weave.api`.

## Non-Goals

`weave` does not provide Hydra defaults lists, global config groups, a first-party
CLI executable, untrusted config sandboxing, workflow execution, queueing, stage
execution, or run-store persistence.
