UV_CACHE_DIR ?= /tmp/uv-cache
export UV_CACHE_DIR
.DEFAULT_GOAL := help

MAKEFILE_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
MAKE_FRAGMENTS := $(sort $(wildcard $(MAKEFILE_ROOT)make/*.mk))

include $(MAKE_FRAGMENTS)
