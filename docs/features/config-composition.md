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
- Commandless config args from project-owned adapters, including scoped-overlay
  shorthand such as `model/=model_B`.
- OmegaConf interpolation with a narrow resolver policy.
- Recipe expansion through `RecipeCatalog`, recipe manifests, and trusted recipe
  plugin loading.
- Secret redaction, provenance, source artifact records, raw source snapshot
  records, composition manifests, and config fingerprints.
- Trusted `_target_` object graph construction via `instantiate(...)`.
- Optional selected-object construction through `ConfigEntrypoint` for explicit
  resolved-config dot paths.

## Public API

```python
from weave import (
    ConfigEntrypoint,
    ConfigError,
    Recipe,
    RecipeCatalog,
    compose_config,
    compose_config_from_args,
    compose_config_with_catalog,
    inspect_config_args,
    inspect_config_composition,
    instantiate,
    register_recipe,
)
```

Detailed commandless result, parse, and base-resolution records are available
from `weave.api`. Retained argv helper names are compatibility helpers: prefer
`compose_config_from_args(...)`, `inspect_config_args(...)`, or
`ConfigEntrypoint` for new adapters.

## Adapter Boundary

Projects own their CLI parser, commands, and command-specific flags. The project
selects a base config directly or through a `ConfigEntrypoint` resolver, then
passes only config args such as `model/=model_B` and `trainer.epochs=5` to
`weave`. `compose_args(...)` and `inspect_args(...)` default to an empty explicit
config-arg sequence and never read `sys.argv`.

## Non-Goals

`weave` does not provide Hydra defaults lists, global config groups, a first-party
CLI executable, untrusted config sandboxing, workflow execution, queueing, stage
execution, run-store persistence, implicit `sys.argv` parsing, or full-config
instantiation.
