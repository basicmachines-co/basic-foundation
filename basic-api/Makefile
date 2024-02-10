.PHONY: install test clean lint format lint-fix

install:
	poetry install

test:
	poetry run pytest

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix --unsafe-fixes .

format:
	poetry run ruff format .

tailwind:
	npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css
