# Config Behavior Matrix

This matrix records the current Stage 1 public behavior for project-owned config
adapters.

| Area | Current behavior | Validation evidence | Deferred or rejected behavior |
| --- | --- | --- | --- |
| Commandless config args | Projects pass explicit config args to `compose_config_from_args(...)`, `inspect_config_args(...)`, or `ConfigEntrypoint.compose_args(...)`. | Unit and integration config-args tests; project-owned adapter example. | Weave-owned command parsing and implicit `sys.argv` reads. |
| Scoped overlays | `scope/=name` and `+scope/=name` apply scoped overlay files before recipe expansion. | Integration scoped-overlay tests and `project-cli-argv` example. | Hydra defaults lists or global config groups. |
| Retained argv helper names | `compose_config_from_argv(...)` and `inspect_config_from_argv(...)` accept explicit base-first vectors or raise migration diagnostics for old command-first shapes. | Migration-diagnostic integration tests and adapter example. | Public command-first helper semantics and `command_choices`. |
| Config entrypoint | `ConfigEntrypoint` composes or inspects explicit config args with exactly one base strategy. | Integration tests for fixed base, resolver base, and examples. | Global config search, package root discovery, or first-party process policy. |
| Base resolver | Resolver receives `ConfigBaseRequest(base_context=...)` and returns `ConfigBaseResolution(base_config_path=..., details=...)`. | Unit/integration resolver tests and adapter example. | Serializing opaque `base_context` or command-specific resolver arguments. |
| Selected instantiation | Explicit dot paths or caller-name-to-dot-path mappings instantiate selected resolved values after composition. | Unit/integration selected-instantiation tests and adapter example. | Default instantiation, full-config instantiation, or automatic target discovery. |
| Plain-data export | Commandless result `to_dict()` contains stable metadata and composed/inspection data; Python objects stay in `objects` only. | Contract tests for result shape and object exclusion. | Serializing Python objects or opaque project context. |
| Import boundary | Ordinary `import weave` stays lazy and does not import downstream target modules. | Package import tests. | Heavy runtime dependencies or downstream project imports at package import time. |
| Artifact defaults | Source artifacts, provenance, redaction, raw snapshot references, and artifact-safe fingerprints remain deterministic. | Contract and integration artifact suites. | Persisting resolved configs or raw source bytes by default. |
