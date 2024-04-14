# basic-foundation

Opinionated Foundation Boilerplate for a SaaS Platform

* Boring tech
* Reproducible builds
* Development flow
* 100% test coverage
* Easy to extend

## Assumptions

* Requires a python installation (recommend python [3.12](https://docs.python.org/release/3.12.1/whatsnew/3.12.html))
* Github access https://docs.github.com/en/get-started/quickstart/set-up-git
* IDE (.idea) file is included

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

cd basic-api

```bash
poetry init
```

enter the poetry shell

```bash
poetry shell
```

## start service

cd basic-api/src

```bash
uvicorn basic_api.main:app --reload
```

### Setup the frontend

## deploy to render.com

* Signup/Login to render.com dashboard
* Select "New Blueprint"
* Choose the basic-foundation repo from the list and click the "Connect" button
* View the service on the [dashboard](https://dashboard.render.com/)
