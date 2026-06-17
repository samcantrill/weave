# Testing

Local validation is intentionally package-local and dependency-light.

```sh
make validate-pr
make test-summary
```

Suite targets:

- `make test-package`
- `make test-unit`
- `make test-contract`
- `make test-integration`
- `make test-examples`

`make test-summary` writes `build/test-summary.md` with suite-level evidence.
Tests should keep `weave` import-safe, preserve deterministic artifact contracts,
and avoid domain-specific examples.
