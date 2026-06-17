.PHONY: test test-package test-unit test-contract test-integration test-examples test-all test-summary

test: test-package test-unit test-contract test-integration

test-package:
	UV_CACHE_DIR=$(UV_CACHE_DIR) PYTHONPATH=src uv run --group dev python -m pytest tests -m package --ignore=tests/test_examples.py

test-unit:
	UV_CACHE_DIR=$(UV_CACHE_DIR) PYTHONPATH=src uv run --group dev python -m pytest tests/unit

test-contract:
	UV_CACHE_DIR=$(UV_CACHE_DIR) PYTHONPATH=src uv run --group dev python -m pytest tests/contracts

test-integration:
	UV_CACHE_DIR=$(UV_CACHE_DIR) PYTHONPATH=src uv run --group dev python -m pytest tests/integration

test-examples:
	UV_CACHE_DIR=$(UV_CACHE_DIR) PYTHONPATH=src uv run --group dev python -m pytest tests/test_examples.py

test-all: test test-examples

test-summary:
	UV_CACHE_DIR=$(UV_CACHE_DIR) PYTHONPATH=src uv run --group dev python -m tools.test_harness summary
