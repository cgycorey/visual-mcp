.PHONY: help install test lint format type-check clean build wheel dev example

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  type-check  Run type checking"
	@echo "  clean       Clean all caches and build artifacts"
	@echo "  build       Build package"
	@echo "  wheel       Quick wheel build for MCP testing"
	@echo "  dev         Run development server"
	@echo "  example     Run example script"

install:
	uv sync --all-extras
	uv run pre-commit install

test:
	uv run pytest tests/ -v --cov=src/visual_mcp

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

type-check:
	uv run mypy src/ tests/

clean:
	uv cache clean
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

build: clean
	uv build

wheel:
	uv build

dev:
	uv run mcp dev src/visual_mcp/server.py

example:
	uv run python examples/example_usage.py