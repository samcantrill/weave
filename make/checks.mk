.PHONY: lint typecheck format validate-pr

lint:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --group dev ruff check .

typecheck:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --group dev pyright .

format:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv run --group dev ruff format .

validate-pr: lint typecheck test-all build
