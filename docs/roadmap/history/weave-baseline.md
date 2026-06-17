# Weave Baseline History

`weave` defines a trusted config authoring surface: YAML composition,
overlays, includes, replacement, overrides, recipes, target instantiation,
redaction, provenance, manifests, source artifacts, raw source snapshots, and
config fingerprints.

Key decisions preserved in this repository:

- Keep the public import surface centered on `import weave`.
- Duplicate small config-owned helper behavior instead of creating a shared core
  utility package.
- Keep authored configs trusted; do not add an untrusted-config sandbox.
- Keep deterministic artifact behavior covered by golden fixtures.
