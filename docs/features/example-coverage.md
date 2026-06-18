# Example Coverage

Runnable examples are validated by `make test-examples` through
`tests/test_examples.py::test_weave_example_script_runs`. Example manifests point
back to this shared validation command.

| Example | Coverage | Stage 1 relevance |
| --- | --- | --- |
| `config-composition.basic` | Base config, overlays, update/add overrides, and resolved/unresolved/redacted views. | Core composition behavior used by commandless helpers. |
| `config-composition.includes` | Local includes, nested include context, include replacement, and include source artifacts. | Confirms authored config composition remains independent of adapter shape. |
| `config-composition.replacement-overlays` | Multi-overlay order and `_replace_: true`. | Documents deterministic overlay behavior. |
| `config-composition.errors` | Structured errors for missing includes, invalid include overrides, unsupported resolvers, and unsupported `_copy_`. | Shows plain-data error context conventions. |
| `recipes` | Recipe registration, expansion, overlays, overrides, interpolation, manifest output, redaction, and fingerprints. | Confirms config args still feed existing recipe behavior. |
| `artifact-safety` | Metadata-only source artifacts, provenance, redaction, resolver facts, fingerprints, and raw snapshot opt-in. | Records artifact-safe defaults preserved by Stage 1. |
| `target-instantiation` | Explicit construction of trusted `_target_` object graphs with nested targets, `_args_`, `_partial_`, and `_inject_`. | Separates explicit object construction from composition. |
| `project-cli-argv` | Project-owned config args, scoped overlays, passthrough args, warnings, resolver metadata, selected instantiation, and migration diagnostics. | Main Stage 1 adapter example. |

## Deferred Example Topics

The examples intentionally do not cover first-party CLI execution, command
semantics, global config search, full-config instantiation, workflow execution,
stores, schedulers, datasets, metrics, or domain-specific pipelines. Those topics
remain outside the Stage 1 contract.
