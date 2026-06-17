# Architecture

`weave` owns configuration authoring behavior for trusted Python projects. It
loads and composes config files, expands recipes, resolves interpolation,
instantiates trusted `_target_` object graphs, redacts secret-like values, and
returns auditable plain-data records.

## Boundaries

`weave` must not import downstream project packages during ordinary
package import. Project code may import `weave`; `weave` may import project code
only when trusted config explicitly asks for recipe loading or `_target_`
instantiation.

`weave` is not a workflow engine. It does not schedule work, run stages, own run
stores, manage queues, or define domain-specific schemas.

## Source Layout

```text
src/weave/        runtime package
tests/            package, unit, contract, integration, and example tests
examples/         runnable authoring examples
docs/             feature docs and roadmap history
tools/            local development tools
```

## Dependency Policy

Runtime dependencies are intentionally small: OmegaConf, Pydantic, and PyYAML.
New runtime dependencies should be added only when they serve config authoring
behavior directly and cannot reasonably remain optional or downstream-owned.
