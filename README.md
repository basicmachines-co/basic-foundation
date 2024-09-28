# Basic Foundation

![Build Status](https://github.com/basicmachines-co/basic-foundation/actions/workflows/basic-foundation-test.yml/badge.svg)
![License](https://img.shields.io/github/license/basicmachines-co/basic-foundation)
![Version](https://img.shields.io/github/v/release/basicmachines-co/basic-foundation)
![Coverage](https://codecov.io/gh/basicmachines-co/basic-foundation/branch/main/graph/badge.svg)

## Overview

Basic Foundation is a Python framework for building full-stack SaaS applications. It provides user authentication, APIs,
and user management using modern Python technologies, including FastAPI, PostgreSQL, and HTMX.

## Tech Stack

- **Modern Python**: Python 3.12 for improved typing support, error messages, and performance.
- **Type Hints and Type Checking**: Comprehensive type hints with Pyright configured for type checking during
  development.
- **Async FastAPI**: All API operations are implemented asynchronously using `async`/`await` and non-blocking I/O.
- **PostgreSQL**: Database layer for persistence.
- **SQLAlchemy**: Async DB layer with SQLAlchemy 2.0 for ORM.
- **HTMX**: Frontend admin web app with dynamic interactions via HTMX.
- **TailwindCSS**: Utility-first styling for the admin interface.
- **Testing**: Comprehensive test coverage for core app and API using Pytest.
- **Playwright**: End-to-end in-browser testing for the admin web app.

## Features

- **Asynchronous API Implementation**: FastAPI for non-blocking I/O and async database access.
- **JWT Authentication**: Secure token-based authentication for both API and web endpoints.
- **RESTful API Module**: Comprehensive user management and authentication via API.
- **Responsive Web UI**: Server-side rendered admin UI with partial page updates using Jinja2 templates and HTMX.
- **TailwindCSS**: Modular and customizable styles using TailwindCSS.
- **Email Integration**: SMTP support for sending account-related emails (password recovery, activation).
- **Docker Compose**: Configured for local development with Postgres 15.
- **DBMate for Migrations**: Easy schema migrations with DBMate, including schema versioning, rollback, and SQL schema
  dumping.
- **Transactional Tests**: Rollback transaction after each test to ensure isolated test environments.
- **100% Test Coverage**: Test coverage measurement with reporting via Coverage.py.
- **End-to-End Testing**: Playwright tests for frontend functionality, including interactive elements.
- **CI/CD with GitHub Actions**: Automated testing, versioning, and deployment with GitHub Actions. Releases include
  version bumps, migrations, and automated deployment (Render.com).
- **Preview Environments**: Each branch or pull request is deployed to an isolated environment via Render.com.

## Developers

This framework was created as a starter kit for building SaaS applications. It contains essential features for any
platform, such as user authentication and management. There are lots of other similar projects already (
see [References]), but they did not have some of the features that I was really looking for, including modern async
Python, fully featured testing, and HTMX integration for building full-stack web apps. Additionally, I've added elements
based on my software engineering experience that are essential for maintainable projects, like continuous integration,
robust testing, and release automation and deployment.

The goal of this project is to provide a starting point for building applications using my preferred technology stack (
FastAPI, SQLAlchemy, Postgres, HTMX) without having to reinvent the wheel for every feature. I've incorporated a lot of
learnings from other projects and designed patterns that are meant to be extensible and maintainable.

### Good Code (Instead of No-Code)

Basic Foundation is designed to encourage writing maintainable, high-quality code. Instead of focusing on low-code or
no-code solutions, this project prioritizes clarity, explicitness, and structure that can easily be extended or
modified. This is essential for developers to maintain full control over their code without relying on black-box
solutions.

### FastAPI and HTMX for Server-Side Full-Stack Web Apps

HTMX allows for dynamic updates to web pages without the need for heavy front-end frameworks. By focusing on server-side
rendering with partial updates, HTMX provides the interactivity expected in modern applications while still leaving
application logic on the server. FastAPI, because it's based on Starlette, is well suited to creating HTML-based
endpoints to handle partial data updates and deliver HTML back to the client to update the DOM in the browser. This
project contains implementation examples for many HTMX patterns, including click-to-edit, lazy loading, notifications,
dialogs, and dynamic partial elements.

### Modular Project Structure

The codebase is organized into modules that separate concerns cleanly. Each module contains its own routes, business
logic, and tests. This modularity makes it easy to add new features or swap out parts of the stack without affecting the
core of the application. Database access, basic CRUD operations, pagination, and security are already implemented.
Developers can also create new modules or services as needed, with clear patterns to follow.

### Easy Deployment to Cloud Environments

The project is built with deployment in mind. Using Docker and GitHub Actions, you can easily set up automated
deployment pipelines to cloud platforms like Render.com. Preview environments are automatically generated for each pull
request, making it easier to test and view changes in a live environment before merging.

### Own All of Your Own Data and Essential Features

There are many options for managing users and authentication, including third-party applications and services. I've used
some in the past and have always found it to be a mistake ([Auth0](https://auth0.com/)). Users and authentication are
core functionalities for most SaaS applications and too important to outsource. They are tightly integrated with every
part of the application stack. They are also easy to get wrong, with severe security consequences. At the same time,
authentication and user management do not deliver much value on their own. Frameworks like FastAPI
have [great information](https://fastapi.tiangolo.com/tutorial/security/first-steps/) on how to build security and
authentication, but it still takes time and can be tricky.

### Postgres for All the Data

PostgreSQL is used for persistent data storage because it is reliable, performant, flexible, and available everywhere.
The project is set up with PostgreSQL 15 for development via Docker Compose, offering advanced features like JSONB,
full-text search, and many other features. DBMate handles schema migrations easily using only SQL. The database schema
is managed outside of application code.

### Test Everything

Basic Foundation includes comprehensive testing with Pytest and Playwright to ensure your app is reliable. Tests cover
all core functionality, including authentication, API endpoints, and frontend interactions. Transactional tests ensure
each test runs in isolation, rolling back database changes at the end of every test (except for Playwright tests).
Coverage reports ensure that important parts of the codebase aren’t missed.

### MIT License

Basic Foundation takes a lot of inspiration from other works and is licensed to be used freely under the MIT License,
allowing anyone to use, modify, and distribute it, including for commercial purposes. By choosing an open-source
framework, you avoid being locked into commercial SaaS starter frameworks. This project provides the flexibility and
freedom to build your project on your own terms, without licensing or vendor lock-in.

## References

- https://github.com/fastapi/full-stack-fastapi-template
- https://github.com/whythawk/full-stack-fastapi-postgresql/blob/master/docs/development-guide.md
- https://github.com/mjhea0/awesome-fastapi
- https://max.engineer/server-informed-ui
- https://htmx.org/essays/splitting-your-apis/
- https://htmx.org/essays/why-tend-not-to-use-content-negotiation/

## Contributing

Contributions are welcome! If you’re interested in contributing to Basic Foundation, follow these steps:

1. **Fork the repository** and clone it locally.
2. **Create a new branch** for your feature or bugfix.
3. **Ensure tests pass** and add new tests where needed.
4. **Submit a pull request** with a clear explanation of your changes.

Please check the [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## Requirements

- Python (3.12): required for generics and type hinting
- Docker/Docker compose: run Postgres instance locally via Docker Compose
- GitHub: the `gh` [CLI tool](https://cli.github.com/) is used for releases
