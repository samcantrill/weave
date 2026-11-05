# Fingerprints And Artifacts

`weave` records deterministic config artifacts so callers can compare authored
configuration behavior without persisting raw secrets by default.

Core records include:

- `CompositionManifest`
- `SourceArtifactRecord`
- `RawSourceSnapshotBundle`
- `ConfigFingerprintRecord`
- recipe manifest entries
- final value authorship and provenance metadata

Artifact-safe fingerprints use redacted and metadata-rich composition facts.
Raw source snapshots are opt-in; metadata-only source records are the default.

The `artifact_safe_authored_composition_v2` policy (payload version 2) encodes
redacted configuration values using `weave.ordered-config.v1`. Nested mapping
order therefore affects identity even when source facts are identical. Existing
version-1 records remain readable but compare as `incompatible_policy`; their
lost mapping order is never inferred or rewritten.

For executable configuration values, use `ordered_config_fingerprint(value)`.
It hashes the same versioned ordered encoding used for transport, preserving list
duplicates and distinguishing reordered mappings or sequences. This digest
contains runtime values if the caller supplies them; it does not perform
redaction and must not replace the artifact-safe policy for public provenance.
Generic `hash_mapping` and canonical protocol JSON retain their existing
key-sorting behaviour; neither alone represents configuration order.
