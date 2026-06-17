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
