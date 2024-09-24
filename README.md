# basic-foundation

![Build Status](https://github.com/basicmachines-co/basic-foundation/actions/workflows/basic-foundation-test.yml/badge.svg)

Opinionated Foundation Boilerplate for a SaaS Platform

- Boring tech
- Reproducible builds
- Development flow
    - easy deployment
    - preview builds
- 100% test coverage
- Easy to extend

tech

- fastapi
- postgresql
- htmx
- tailwind.css

## Assumptions

- Requires a python installation (recommend python [3.12](https://docs.python.org/release/3.12.1/whatsnew/3.12.html))
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
