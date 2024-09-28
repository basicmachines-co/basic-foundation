ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: install test clean lint lint-fix format migrate-new migrate-up migrate-down migrate-dump migrate-reset

install: install-python install-node

install-python:
	poetry install

install-node:
	cd modules/foundation/web && npm install

reset-cov:
	rm -f .coverage

test: reset-cov test-foundation test-modules-api test-modules-web

COVERAGE_ARGS ?= --cov-append --cov-report=term-missing --cov-config=.coveragerc

test-foundation:
	poetry run pytest foundation --cov=./foundation $(COVERAGE_ARGS)

test-modules-api:
	poetry run pytest modules/foundation/api --cov=./modules/foundation/api $(COVERAGE_ARGS)

test-modules-web:  # runs playwright tests: assumes app is running on at API_URL in config
	poetry run pytest modules/foundation/web --cov=./modules/foundation/web $(COVERAGE_ARGS) -m "playwright" --tracing=retain-on-failure
	#poetry run pytest -m "playwright" --headed --slowmo 500

test-coverage:
	poetry run coverage report --fail-under=100

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
	cd modules/foundation/web && npx prettier templates --write

format: format-python format-prettier

type-check:
	poetry run pyright

tailwind:
	cd modules/foundation/web && npm run build

tailwind-prod:
	cd modules/foundation/web && npm run build-prod

# Database migrations

# Database URL (customize according to your environment)
MIGRATE_DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=disable"

# Path to migrations directory
DB_DIR="./db"
MIGRATIONS_DIR="$(DB_DIR)/migrations"

# Create a new migration
# make migrate-new name=create_users_table
migrate-new:
	npx dbmate new $(name)

migrate: migrate-up

# Run all pending migrations
migrate-up:
	echo "database url: $(MIGRATE_DATABASE_URL)"
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u $(MIGRATE_DATABASE_URL) up

# Rollback the latest migration
migrate-down:
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u $(MIGRATE_DATABASE_URL) down

# dump the schema.sql file

migrate-dump:
	@npx dbmate -s "$(DB_DIR)/schema.sql" -u $(MIGRATE_DATABASE_URL) dump

# Rollback all migrations
migrate-reset:
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u DATABASE_URL=$(MIGRATE_DATABASE_URL) drop
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u DATABASE_URL=$(MIGRATE_DATABASE_URL) up

migrate-render:
	echo "database url: $(DATABASE_URL)"
	@npx dbmate -d $(MIGRATIONS_DIR) -s "$(DB_DIR)/schema.sql" -u $(DATABASE_URL) up

init-data:
	poetry run python foundation/tools/init_data.py

run:
	poetry run fastapi run foundation/app.py  --port 10000
