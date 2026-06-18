# Glossary

| Term | Meaning | Notes |
| --- | --- | --- |
| Authored config | YAML or override input written by a trusted project. | `weave` does not sandbox authored configs. |
| Raw config | A config source before composition, interpolation, recipe expansion, or overrides. | Used for source records and raw snapshots. |
| Composed config | The result returned by `weave.compose_config(...)` or commandless config-arg helpers. | Contains resolved, unresolved, redacted, provenance, manifest, and fingerprint data. |
| Resolved config | The final plain-data view after interpolation and validation. | Returned to callers; persistence is caller-owned. |
| Config args | Explicit config shorthand tokens supplied by a project adapter. | Parsed by `compose_config_from_args(...)`, `inspect_config_args(...)`, and `ConfigEntrypoint`. |
| Project-owned adapter | Downstream code that owns CLI parsing, base selection, and process behavior before calling `weave`. | `weave` does not provide a first-party executable. |
| Overlay | A config file merged on top of an earlier config. | Recursive merge by default; `_replace_: true` replaces a mapping. |
| Scoped overlay config arg | Project adapter shorthand such as `model/=model_B`. | Applies an overlay under a config path before recipe expansion. |
| Include | `_include_` directive that loads another local or `file://` config mapping. | Resolved relative to source context. |
| Recipe | Trusted Python object or function that expands a compact config block into explicit config. | Registered in a `RecipeCatalog` or loaded through recipe entry points. |
| Target | `_target_` import path used for trusted object construction. | Instantiated by `weave.instantiate(...)` or selected `ConfigEntrypoint` paths. |
| Selected object | A caller-named result object constructed from an explicit resolved-config dot path. | Stored in `ConfigArgsCompositionResult.objects` and excluded from `to_dict()`. |
| Source artifact | Plain-data record describing an authored source that influenced composition. | Used by manifests, provenance, and fingerprints. |
| Artifact-safe fingerprint | Deterministic fingerprint over redacted/auditable composition facts. | Avoids raw secret values by default. |
