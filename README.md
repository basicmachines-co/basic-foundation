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

### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python -
```

Set the virtual env to be local to the project

```
virtualenvs.in-project
```

cd basic-api

```bash
poetry init
```

enter shell

```bash
poetry shell
```

## start service

cd basic-api/src

```bash
uvicorn basic_api.main:app --reload
```

## deploy to render.com

* Signup/Login to render.com dashboard
* Select "New Blueprint"
* Choose the basic-foundation repo from the list and click the "Connect" button
* View the service on the [dashboard](https://dashboard.render.com/)

Further steps:

* View service details, enable preview environments
* Enable health checks
* Disable auto-deploy on git commit
* Add render deploy hook to github pipeline for git commit
* Use Docker builds and deploys for render
