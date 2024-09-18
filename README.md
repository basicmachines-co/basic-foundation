# basic-foundation

Opinionated Foundation Boilerplate for a SaaS Platform

- Boring tech
- Reproducible builds
- Development flow
- 100% test coverage
- Easy to extend

tech

- fastapi
- htmx
- tailwind.css

## Assumptions

- Requires a python installation (recommend python [3.12](https://docs.python.org/release/3.12.1/whatsnew/3.12.html))
- Github access https://docs.github.com/en/get-started/quickstart/set-up-git
- IDE (.idea) file is included

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

cd basic-foundation

```bash
poetry init
```

enter the poetry shell

```bash
poetry shell
```

## start service

cd basic-app/src

```bash
uvicorn app.main:app --reload
```

## deploy to render.com

- Signup/Login to render.com dashboard
- Select "New Blueprint"
- Choose the basic-foundation repo from the list and click the "Connect" button
- View the service on the [dashboard](https://dashboard.render.com/)

## todo

- [x] deploy to render
- [x] add fastapi-users
- [x] transactional tests
- [x] add fastapi-users endpoint tests
- [x] cleanup app.py - split users into module/apirouter
- [x] add htmx
- [-] jinjaX - https://jinjax.scaletti.dev/
- [x] makefile
- [x] upgrade to pydantic v2 (newer fastapi?)
- [x] .env for config
- [x] code linting/formatting: ruff
- [x] postgres instead of sqlite
- [x] fix registration flow
- [x] fix tests
- [x] logging
- [x] configure postgres on gitlab actions
- [x] configure postgres on render.com
- [x] db migrations
- [x] add styling - tailwind/flowbite
    - [x] alpine
    - [x] tailwind plugins
    - [x] login
    - [x] register
- [x] replace auth
    - remove fastapi-users
    - replace with vanilla auth
- [-] shadcn components
- [x] crud users
- [ ] test coverage
    - codecov https://github.com/marketplace/codecov/plan/MDIyOk1hcmtldHBsYWNlTGlzdGluZ1BsYW4xNg==#plan-16
- [x] csrf - https://github.com/simonw/asgi-csrf
- [x] view profile
- [x] app user management
    - click to edit forms: https://htmx.org/examples/click-to-edit/
    - icons: https://github.com/sirvan3tr/jinja-primer-icons
    - example: render.com dashboard
    - https://devdojo.com/wave#demo
- [x] forgot password flow
- [ ] mailapi - sendgrid? or mailgun?
    - https://sabuhish.github.io/fastapi-mail/example/
    - https://pramod4040.medium.com/fastapi-forget-password-api-setup-632ab90ba958
- [ ] branch deploys (preview environments)
- [ ] stripe integration
- [ ] webhooks
- [ ] queueing
- [ ] dependabot
- [ ] sentry
- [ ] codecov
- [ ] static object storage
    - https://docs.render.com/deploy-minio
    - run minio
      locally https://ktyptorio.medium.com/simple-openweather-api-service-using-fastapi-and-minio-object-storage-docker-version-f3587f7eb3de
- [ ] multi tenant
- [ ] postgres row level security
- [-] web components
    - lit
    - shoelace
- [ ] dockerfile - https://inboard.bws.bio/?
- [ ] deploy docker to render
    - https://docs.render.com/docker
- [x] install fastapi-jwt (https://github.com/k4black/fastapi-jwt/)
- [x] implement examples from fastapi-jwt:
    - https://k4black.github.io/fastapi-jwt/user_guide/examples/
    - https://k4black.github.io/fastapi-jwt/
- [x] clone https://github.com/tiangolo/full-stack-fastapi-template
- [x] implement user db schema, models, tests
- [x] add initial super user via init with hashed password
- [x] implement users routes, tests
- [x] implement auth api routes, tests
- [x] implement emails
- [x] refactor to app.core
- [x] refactor to app.users
- [x] refactor to app.auth
- [x] recover password routes
- [x] refactor app base package to foundation
- [x] use fastapi cli command
- [x] refactor service code
    - send emails
    - reset pass
    - return Errors from service
- [x] modify frontend routes
- [ ] remove all print() calls
- [-] add faastapi-problems for error responses: https://github.com/NRWLDev/fastapi-problem
- [x] remove fastapi-users
- [ ] package as separate modules?
    - core
    - api
    - web-htmx
- [ ] permission checks
    - [ ] user service with current user
    - [ ] has to be at least one admin
    - [ ] only admins can create/edit users
    - [ ] db: rename is_superuser to is_admin
- [ ] frontend
    - [x] crud users happy path
    - [x] reset password flow
    - [x] user profile
    - [x] pagination for users list
    - [x] dashboard page
    - [x] use pydantic models for form
        - use ids in form post
        - use one route for get/post for html pages
    - [x] refactor web route files for cleanup
    - [-] daisyui
    - [x] htmx
        - [x] 404 page
        - [x] 500 page
        - [-] oob swap for name after updating detail
        - [-] db exception in error message
    - [ ] playwrite tests for html flow
        - [ ] login
        - [ ] password reset
        - [ ] dashboard
        - [ ] list users
        - [ ] view user
        - [ ] edit user
        - [ ] add user
        - [ ] delete user
        - [ ] edit profile
        - [ ] logout
        - [ ] fixup styles for mobile
    - [ ] refactor
        - [x] try/catch/finally in db dep
        - [ ] error handling in services
        - [x] stacked navbar layout
        - [ ] 422 error on page load - http://127.0.0.1:8000/reset-password
        - [ ] fasthx
            - [ ] redo flash message
                - edit success
                - edit error
            - [-] remove Jinja2Blocks
            - [x] edit password
            - [ ] fix delete user
            - [ ] remove shadow from rounded borders
            - [ ] clean up tailwind styles
            - [ ] user name update oob on edit success

## references

- https://github.com/mjhea0/awesome-fastapi
- https://github.com/whythawk/full-stack-fastapi-postgresql/blob/master/docs/development-guide.md
