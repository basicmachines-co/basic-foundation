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

# dbmate docker image
DBMATE_IMAGE=amacneil/dbmate

# Create a new migration
# make new-migration name=create_users_table
new-migration:
	@docker run --rm -v $(shell pwd)/$(MIGRATIONS_DIR):/db/migrations $(DBMATE_IMAGE) new $(name)

# Run all pending migrations
migrate-up:
	@docker run --rm -v $(shell pwd)/$(MIGRATIONS_DIR):/db/migrations --network="host" -e DATABASE_URL=$(DATABASE_URL) $(DBMATE_IMAGE) -s "./db/schema.sql" up

# Rollback the latest migration
migrate-down:
	@docker run --rm -v $(shell pwd)/$(MIGRATIONS_DIR):/db/migrations --network="host" -e DATABASE_URL=$(DATABASE_URL) $(DBMATE_IMAGE) -s "./db/schema.sql" down

# dump the schema.sql file
migrate-dump:
	docker run --rm -v $(shell pwd)/db:/db --network="host" -e DATABASE_URL=$(DATABASE_URL) $(DBMATE_IMAGE) -s "./db/schema.sql" dump

# Rollback all migrations
migrate-reset:
	@docker run --rm -v $(shell pwd)/$(MIGRATIONS_DIR):/db/migrations --network="host" -e DATABASE_URL=$(DATABASE_URL) $(DBMATE_IMAGE) -s "./db/schema.sql" drop
	@docker run --rm -v $(shell pwd)/$(MIGRATIONS_DIR):/db/migrations --network="host" -e DATABASE_URL=$(DATABASE_URL) $(DBMATE_IMAGE) -s "./db/schema.sql" up

# Note: The `--network="host"` option is used to allow the Docker container to access the host network.
# This is necessary for the container to connect to the local database.
# You might need to adjust this depending on your Docker setup and database location.
