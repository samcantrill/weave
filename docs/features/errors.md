# Errors

`weave.errors.ConfigError` is the package-owned root for configuration errors.
Concrete errors carry structured `ConfigErrorContext` payloads where useful so
callers can display diagnostics without parsing message text.

Primary error families include load, merge, override parse/apply,
interpolation, validation, include resolution/expansion, recipe registration and
expansion, target import/instantiation, redaction, provenance, artifact, and
fingerprint errors.

Downstream adapters that embed `weave` are responsible for mapping these errors
into their own CLI or runtime diagnostics.
