.PHONY: run test lint format

run:
	uvicorn src.api.main:app --reload

test:
	pytest tests/

lint:
	ruff check src/

format:
	ruff format src/

install:
	pip install -r requirements.txt