# basic-foundation

![Build Status](https://github.com/basicmachines-co/basic-foundation/actions/workflows/basic-foundation-test.yml/badge.svg)

### Overview

Basic Foundation is designed for developers building web applications and APIs in Python. It takes advantage of Python
3.12’s type hinting and async capabilities for scalability and performance. The project includes transactional database
tests, ensuring that the real database logic is tested and not just mocked. With built-in JWT authentication, API, and
web modules, and a pre-configured CI/CD pipeline, it streamlines setting up the infrastructure needed for a typical SaaS
project. Additionally, full test coverage and support for dynamic preview environments reduce the chances of bugs and
make deployments safer.

## Features of Basic Foundation

- **Python 3.12 with Type Hints**: The project uses Python 3.12 and includes type hints throughout the codebase. Pyright
  is configured to perform type checking during development, ensuring that types are correctly enforced. This reduces
  runtime errors by catching type mismatches early.
- **100% Asynchronous APIs**: All API operations are asynchronous, implemented with FastAPI and async SQLAlchemy. This
  setup allows non-blocking I/O, which improves performance and scalability when handling multiple concurrent requests,
  such as during API-heavy workloads.
- **Transactional Tests with Rollbacks**: Instead of relying on mock objects, database tests are run in real
  transactions that are rolled back after the test completes. This ensures that each test starts with a clean database
  state while still exercising the full application stack, making it possible to catch more bugs and integration issues.
- **Authentication and User Management**: The application includes JWT-based authentication, with functionality for user
  registration, login, and subscription management. These are implemented as modular components that can be extended to
  fit project-specific requirements.
- **API Module**: The API module exposes endpoints for core business logic, including user management and subscription
  handling. Built using FastAPI, it offers an easy way to extend or add new APIs while maintaining clear separation
  between the web and API layers.
- **Web Module**: Server-side rendering is handled using Jinja2 templates, while HTMX is used to enhance the user
  experience with partial page updates. TailwindCSS is used for styling to minimize the need for custom CSS. This
  approach keeps the frontend simple, while still supporting dynamic updates.
- **Email Integration**: The project includes email sending via SMTP, enabling the app to send account-related emails
  such as password recovery or account activation. This feature simplifies integrating email functionality without
  third-party services.
- **Database Migrations with DBMate**: Database schema changes are handled by DBMate, which provides simple migration
  commands for PostgreSQL. It ensures that schema changes can be applied, rolled back, and dumped consistently across
  different environments.
- **100% Test Coverage**: Every core library, API endpoint, and web component has full test coverage. Tests are written
  using pytest, ensuring that all critical paths are tested. This helps catch regressions and bugs early in the
  development process.
- **Playwright for Frontend Testing**: Playwright is used for testing frontend functionality, including interactive
  features like forms and modals. These tests ensure that the frontend behaves as expected across different browsers and
  devices.
- **Continuous Integration and Deployment (CI/CD)**: GitHub Actions is used for automated testing, versioning, and
  building of the project. Each release includes automated version bumps, database migrations, and deployment to
  Render.com or other platforms.
- **Preview Environments**: The project supports preview environments using Render.com’s feature, allowing each pull
  request or branch to deploy its own isolated environment. This is useful for testing changes before merging them into
  the main branch.
- **TailwindCSS for Styling**: Minimal CSS is used in favor of TailwindCSS, which provides utility-based styling. This
  keeps the styles consistent and reduces the complexity of managing custom CSS.

## Assumptions

- Requires a python installation (3.12)
- Github access https://docs.github.com/en/get-started/quickstart/set-up-git
- Docker/Docker compose

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

https://pipx.pypa.io/stable/

```bash
brew install pipx
pipx ensurepath
sudo pipx --global ensurepath  # optional to allow pipx actions with --global argument
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
