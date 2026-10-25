.PHONY: test lint lint-fix format format-check typecheck architecture openapi codegen check ci

test:
	uv run --locked poe test

lint:
	uv run --locked poe lint
	uv run --locked poe format-check

lint-fix:
	uv run --locked ruff check --fix .
	uv run --locked poe format

format: lint-fix

format-check:
	uv run --locked poe format-check

typecheck:
	uv run --locked poe typecheck

architecture:
	uv run --locked poe architecture

openapi:
	uv run --locked poe openapi

codegen:
	uv run --locked poe codegen

check:
	uv run --locked poe check

ci:
	uv run --locked poe ci
