# weave

`weave` is a typed Python configuration authoring library for trusted projects.
It composes YAML, overlays, includes, recipes, interpolation, commandless config
args, and `_target_` object graphs into audited plain data and optional Python
objects.

The package imports as `weave`:

```python
from weave import ConfigEntrypoint, compose_config, compose_config_from_args, instantiate
```

## Features

- YAML loading with duplicate-key checks and plain-data validation.
- Base configs, overlay files, strict dot-path overrides, and explicit `+` adds.
- Recursive `_include_` composition and `_replace_: true` mapping replacement.
- OmegaConf interpolation with a narrow resolver policy.
- Trusted recipes, recipe catalogs, recipe manifests, and recipe plugin loading.
- Trusted `_target_` object graph instantiation with `_args_`, `_partial_`, and `_inject_`.
- Redaction, provenance, source maps, composition manifests, source artifacts,
  raw source snapshot records, and artifact-safe config fingerprints.
- Project-owned adapter helpers through `ConfigEntrypoint` and
  `compose_config_from_args(...)`; `weave` does not own project commands.
- Optional selected-object instantiation for explicitly selected trusted config
  paths.
- Structured config errors with plain-data context payloads.

`weave` treats authored configs as trusted project code. It is not a workflow
engine, does not execute pipeline stages, and does not provide an untrusted
configuration sandbox.

## Development

```sh
uv sync --all-groups
make validate-pr
make test-summary
```

Useful focused targets:

```sh
make test
make test-examples
make lint
make typecheck
make build
```

Examples live in [`examples/`](examples/README.md). Tests live in [`tests/`](tests/).
Design and roadmap notes live in [`docs/`](docs/).
