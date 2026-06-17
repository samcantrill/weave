# Agent Guide

This repository contains `weave`, a domain-neutral Python package for deterministic
configuration composition, provenance, and object instantiation for trusted
Python projects.

## Working Rules

- Keep runtime package imports minimal; ordinary `weave` import must not import
  downstream project code.
- Treat authored configs as trusted project code, not as untrusted input.
- Keep the package domain-neutral. Do not add domain-specific recipes, stages,
  schemas, datasets, metrics, or analysis behavior.
- Do not introduce heavyweight runtime dependencies without an explicit design
  reason.
- Preserve deterministic artifact behavior unless a compatibility break is
  intentional and documented.
- Use `docs/GLOSSARY.md` for preferred vocabulary.

## Local Checks

Run before preparing a PR:

```sh
make validate-pr
```

Run before writing a PR body:

```sh
make test-summary
```

## Repository Layout

- `src/weave/`: runtime package and public Python APIs.
- `tests/`: package, unit, contract, integration, and example tests.
- `examples/`: runnable authoring examples.
- `docs/`: feature docs, architecture notes, glossary, and roadmap history.
- `tools/`: repository-local development tools only.
