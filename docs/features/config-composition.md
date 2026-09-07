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
- Call-scoped `_resolve_` replacement after composition and before target
  construction.

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
    resolve_structural,
)
```

Detailed commandless result, parse, and base-resolution records are available
from `weave.api`. Retained argv helper names are compatibility helpers: prefer
`compose_config_from_args(...)`, `inspect_config_args(...)`, or
`ConfigEntrypoint` for new adapters.

## Environment Values

All composition and inspection helpers accept the keyword-only
`environment: Mapping[str, str] | None = None`. `ConfigEntrypoint.compose_args`
and `inspect_args` take it per call, so one entrypoint can serve different
configurations concurrently.

- Omit it (or pass `None`) to snapshot `os.environ` before loading configuration.
- Pass a mapping to use only its values. `{}` has no ambient fallback.
- Values and keys must be strings. `oc.env` keeps values as strings, including
  `"0"`, `"false"`, and an empty string. A missing key uses its authored default,
  if present; `${oc.env:NAME,null}` can produce `None`. Without a default it fails.

For a config containing `root: ${oc.env:ROOT}`, concurrent callers can use:

```python
from concurrent.futures import ThreadPoolExecutor
from weave import compose_config


def load(root):
    return compose_config("config.yaml", environment={"ROOT": root}).resolved


with ThreadPoolExecutor(max_workers=2) as pool:
    first, second = list(pool.map(load, ["/machine/a", "/machine/b"]))
```

Weave copies the input before config loading or recipe execution; entrypoints
also capture it before invoking a base resolver. Later changes to the caller's
mapping or shell environment do not change that composition. Weave never
modifies `os.environ` or installs global OmegaConf resolvers. Resolver-like
strings supplied through the environment remain literal data.

This option affects runtime `oc.env` resolution. Include targets still cannot
use resolvers, and other resolver names remain unsupported. Environment values
are not added to provenance, source snapshots, manifests, or artifact-safe
fingerprints; those continue to describe authored configuration. Consequently,
a changed resolved value need not change that fingerprint. The resolved view
contains usable runtime values; apply existing redaction rules before sharing it.

Projects own explicit `.env` parsing and launch environments. This API neither
reads `.env` files nor configures child processes.

## Adapter Boundary

Projects own their CLI parser, commands, and command-specific flags. The project
selects a base config directly or through a `ConfigEntrypoint` resolver, then
passes only config args such as `model/=model_B` and `trainer.epochs=5` to
`weave`. `compose_args(...)` and `inspect_args(...)` default to an empty explicit
config-arg sequence and never read `sys.argv`.

## Structural Resolution Boundary

Composition fixes the authored config, provenance, manifest, and fingerprint.
Runtime values often do not exist yet, so structural resolution is a separate,
explicit call:

```python
import weave

composed = weave.compose_config("config.yaml")
action = composed.resolved["action"]

resolution = weave.resolve_structural(
    action,
    resolvers={
        "example.runtime": weave.StructuralResolverDefinition(
            version=1,
            handler=runtime_resolver,
        )
    },
)

objects = weave.instantiate(resolution.value)
```

An authored directive has one exact envelope and no sibling fields:

```yaml
output_directory:
  _resolve_:
    resolver: example.runtime
    version: 1
    kind: workspace
    workspace_name: primary
```

`weave` owns the `_resolve_` lifecycle, but it does not interpret `kind` or any
other resolver argument. The caller supplies a namespaced implementation for
this call only. There is no global registration, and the `weave.*` namespace is
reserved.

The handler receives a `StructuralResolutionRequest` containing the config
path, exact version, and a deeply immutable copy of only its declared
arguments. It does not receive the config root. It returns finite plain data:
`None`, booleans, integers, finite floats, strings, lists, or string-keyed
mappings. Paths, tensors, arbitrary objects, callables, NaN, and infinity are
rejected. Frozen request containers must be copied back into ordinary lists or
mappings if a handler wants to return them.

Before any handler runs, the complete input is copied and checked for directive
shape, resolver availability, version agreement, and cycles. Nested directives
run before their parent; otherwise ready directives run in stable config-path
order. Resolver-produced `_resolve_` blocks are rejected rather than executed.
Trusted handlers should be read-only lookup or derivation functions because
`weave` cannot undo external side effects performed by Python code.

`StructuralResolutionResult.value` is execution-only and omitted from its
representation. It may contain usable paths or credentials and is not
automatically redacted or persisted. `records` contain ordered, serializable,
recursively redacted declarations and output types, never returned values or
arbitrary exception text. Records have their own schema version and are not
added to `CompositionManifest`.

Calling `resolve_structural(...)` never mutates `ComposedConfig`, its resolved
view, fingerprint, or manifest. Direct `instantiate(...)`, selected-object
construction, and `check_config_targets(...)` all reject unresolved `_resolve_`
nodes before constructing the first target. A resolver may return a `_target_`
mapping; it remains inert until an explicit `instantiate(...)` call.

## Non-Goals

`weave` does not provide Hydra defaults lists, global config groups, a first-party
CLI executable, untrusted config sandboxing, workflow execution, queueing, stage
execution, run-store persistence, implicit `sys.argv` parsing, or full-config
instantiation.
It also does not define domain authorities, search arbitrary root config paths
for resolver dependencies, or register project-specific magic keys.
