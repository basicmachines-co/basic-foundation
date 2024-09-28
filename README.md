# basic-foundation

![Build Status](https://github.com/basicmachines-co/basic-foundation/actions/workflows/basic-foundation-test.yml/badge.svg)

### Overview

Basic Foundation is a starter kit for building SaaS applications in Python. It provides user authentication, APIs, and
user management using modern Python technologies, including FastAPI, PostgreSQL, and HTMX.

### Tech Stack

- **Python 3.12**: Improved typing support, error messages, and performance.
- **Type Hints and Type Checking**: Comprehensive type hints with Pyright configured for type checking during
  development.
- **Async FastAPI**: All API operations are implemented asynchronously using `async`/`await` and non-blocking I/O.
- **PostgreSQL**: Database layer for persistence.
- **SQLAlchemy**: Async DB layer with SQLAlchemy 2.0 for ORM.
- **HTMX**: Frontend admin web app with dynamic interactions via HTMX.
- **TailwindCSS**: Utility-first styling for the admin interface.
- **Testing**: Full test coverage for core app and API using Pytest.
- **Playwright**: End-to-end in-browser testing for the admin web app.
- **GitHub Actions**: CI/CD pipelines for testing and deployment.

### Features

- **Asynchronous API Implementation**: FastAPI for non-blocking I/O and async database access.
- **JWT Authentication**: Secure token-based authentication for both API and web endpoints.
- **RESTful API Module**: Comprehensive user management and authentication via API.
- **Responsive Web UI**: Server-side rendered admin UI with partial page updates using Jinja2 templates and HTMX.
- **TailwindCSS**: Modular and customizable styles using TailwindCSS.
- **Email Integration**: SMTP support for sending account-related emails (password recovery, activation).
- **DBMate for Migrations**: Easy schema migrations with DBMate, including schema versioning, rollback and SQL schema
  dumping.
- **Transactional Tests**: Rollback transaction after each test to ensure isolated test environments.
- **100% Test Coverage**:  Test coverage measurement with reporting via Coverage.py.
- **End-to-End Testing**: Playwright tests for frontend functionality, including interactive elements.
- **CI/CD with GitHub Actions**: Automated testing, versioning, and deployment with GitHub Actions. Releases include
  version bumps, migrations, and automated deployment (Render.com).
- **Preview Environments**: Each branch or pull request is deployed to an isolated environment via Render.com.

## Requirements

- Python (3.12): required for generics and type hinting
- Docker/Docker compose: run postgres instance locally via docker-compose
- GitHub: the `gh` [cli tool](https://cli.github.com/) is used for releases

## Getting started

```bash
brew update
```

### Install python tools

Install pyenv
https://github.com/pyenv/pyenv

```bash
brew install pyenv
```

using pyenv

```bash
pyenv version
```

```bash
brew update
brew install pyenv
eval "$(pyenv init -)"
```

Install python

```bash
pyenv install 3.12
```

set the local dir to use the python version

```bash
pyenv local 3.12
```

Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python -
```

Set the virtual env to be local to the project

```
poetry config virtualenvs.in-project true
```

## Configure project

cd basic-foundation

Install dependencies for python and npm (tailwind)

```bash
make install 
```

Setup the environment

```bash
cp .env.ci .env
```

Run docker-compose (postgres)

```bash
docker compose up
```

Setup database

```bash
make migrate
```

## start service

```bash
make run 
```

Run api tests

```bash 
make test-api
```

Run playwright tests (assume fastapi instance is running on localhost:8000)

```bash 
make test-playwright
```

Enter the poetry shell

```bash
poetry shell
```

## deploy to render.com

- Signup/Login to render.com dashboard
- Select "New Blueprint"
- Choose the basic-foundation repo from the list and click the "Connect" button
- View the service on the [dashboard](https://dashboard.render.com/)

## references

- https://github.com/fastapi/full-stack-fastapi-template
- https://github.com/mjhea0/awesome-fastapi
- https://github.com/whythawk/full-stack-fastapi-postgresql/blob/master/docs/development-guide.md
