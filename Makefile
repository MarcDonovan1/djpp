check:
	uv run ruff check .
	uv run mypy .

fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

sync:
	uv sync

test:
	uv run pytest

run:
	uv run fastapi dev

pipeline: check test