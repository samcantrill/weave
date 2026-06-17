# Contributing

Use [docs/GLOSSARY.md](docs/GLOSSARY.md) for repository vocabulary and preferred
term choices when updating code, docs, tests, or examples.

## Development Setup

```sh
uv sync --all-groups
```

## Checks

Run the local quality gate before preparing a PR:

```sh
make validate-pr
```

`make validate-pr` runs Ruff, Pyright, package tests, example tests, and the
package build. Use `make test-summary` to write suite-level evidence under
`build/test-summary.md`.

Use `make help` to list available targets.

## Scope

Keep `weave` focused on deterministic configuration authoring for trusted
Python projects. Domain-specific recipes, datasets, stages, model classes,
metrics, and analysis logic belong in downstream packages.
