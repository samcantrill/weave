# Argv Shorthand History

Project-CLI argv shorthand was added after standalone extraction so config
semantics could live with `weave` rather than being reimplemented by every
project CLI.

Locked behavior:

- No-slash left-hand sides are value overrides.
- Trailing-slash left-hand sides are scoped overlays.
- Scoped overlays use slash-separated scope paths and optional `+scope/=` add
  mode.
- Scoped overlays apply before recipe expansion; value overrides apply after
  recipe expansion.
- Warnings remain helper-local result data.
- No first-party `weave` CLI executable was added.
