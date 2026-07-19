format:
	uv run ruff check .
	uv run mypy .

sync:
	uv sync

test:
	uv run pytest

run:
	uv run fastapi dev