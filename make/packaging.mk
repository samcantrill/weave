.PHONY: build

build:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv build
