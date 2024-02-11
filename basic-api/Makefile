include ../.env

.PHONY: install test clean lint format lint-fix

install:
	poetry install
	npm install

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


# Database migrations

# Database URL (customize according to your environment)
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=disable"

# Path to migrations directory
MIGRATIONS_DIR=./db/migrations

# Create a new migration
# make migrate-new name=create_users_table
migrate-new:
	npx dbmate new $(name)

# Run all pending migrations
migrate-up:
	@npx dbmate -s "./db/schema.sql" -u $(DATABASE_URL) up

# Rollback the latest migration
migrate-down:
	@npx dbmate -s "./db/schema.sql" -u $(DATABASE_URL) down

# dump the schema.sql file
migrate-dump:
	@npx dbmate -s "./db/schema.sql" -u $(DATABASE_URL) dump

# Rollback all migrations
migrate-reset:
	@npx dbmate -s "./db/schema.sql" -u DATABASE_URL=$(DATABASE_URL) drop
	@npx dbmate-s "./db/schema.sql" -u DATABASE_URL=$(DATABASE_URL) up

# Note: The `--network="host"` option is used to allow the Docker container to access the host network.
# This is necessary for the container to connect to the local database.
# You might need to adjust this depending on your Docker setup and database location.
