# Errors

`weave.errors.ConfigError` is the package-owned root for configuration errors.
Concrete errors carry structured `ConfigErrorContext` payloads where useful so
callers can display diagnostics without parsing message text.

Primary error families include load, merge, override parse/apply,
interpolation, validation, include resolution/expansion, recipe registration and
expansion, target import/instantiation, redaction, provenance, artifact, and
fingerprint errors. `ConfigStructuralResolutionError` covers malformed or
unresolved `_resolve_` directives, missing call-scoped resolvers, exact-version
mismatches, cycles, handler rejection/failure, and invalid resolver outputs.

Structural errors use `source_kind: structural_resolution`,
`source_path: <structural-resolution>`, and `directive: _resolve_`. A resolver
can deliberately reject a request with `StructuralResolverRejected(code=...,
details=...)`; details must be plain data and are recursively redacted. An
unexpected handler exception records only its exception type and a stable
failure code. Its raw message or object representation is never serialized.

Target construction fails with `unresolved_structural_directive` if any input
still contains `_resolve_`. The preflight covers the complete construction set
before the first target runs, preventing partial constructor side effects.

Downstream adapters that embed `weave` are responsible for mapping these errors
into their own CLI or runtime diagnostics.
