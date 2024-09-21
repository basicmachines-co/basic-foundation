include .env

.PHONY: install test clean lint lint-fix format migrate-new migrate-up migrate-down migrate-dump migrate-resetØ

install:
	poetry install
	npm install

test:
	poetry run pytest -m "not playwright"

test-playwright:  # assumes app is running on localhost:8000
	poetry run pytest -m "playwright"

playwright-codegen:
	poetry run playwright codegen http://127.0.0.1:8000/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix --unsafe-fixes .

format-python:
	poetry run ruff format .

format-prettier:
	npx prettier templates --write

format: format-python

tailwind:
	npm run build

tailwind-prod:
	npm run build-prod

# Database migrations

# Database URL (customize according to your environment)
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=disable"

# Path to migrations directory
DB_DIR="./db"
MIGRATIONS_DIR="$(DB_DIR)/migrations"

# Create a new migration
# make migrate-new name=create_users_table
migrate-new:
	npx dbmate new $(name)

# Run all pending migrations
migrate-up:
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u $(DATABASE_URL) up

# Rollback the latest migration
migrate-down:
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u $(DATABASE_URL) down

# dump the schema.sql file
migrate-dump:
	@npx dbmate -s "$(DB_DIR)/schema.sql" -u $(DATABASE_URL) dump

# Rollback all migrations
migrate-reset:
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u DATABASE_URL=$(DATABASE_URL) drop
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u DATABASE_URL=$(DATABASE_URL) up

# Note: The `--network="host"` option is used to allow the Docker container to access the host network.
# This is necessary for the container to connect to the local database.
# You might need to adjust this depending on your Docker setup and database location.

init-data:
	poetry run python app/src/tools/init_data.py

run:
	poetry run fastapi run app/src/foundation/app.py  --port 10000
