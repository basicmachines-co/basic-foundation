# basic-app

Saas platform app using

- fastapi
- htmx
- tailwindUI/Flowbite

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
- [ ] crud users
- [ ] test coverage
    - codecov https://github.com/marketplace/codecov/plan/MDIyOk1hcmtldHBsYWNlTGlzdGluZ1BsYW4xNg==#plan-16
- [ ] playwright
- [ ] csrf - https://github.com/simonw/asgi-csrf
- [ ] view profile
- [ ] app user management
    - click to edit forms: https://htmx.org/examples/click-to-edit/
    - icons: https://github.com/sirvan3tr/jinja-primer-icons
    - example: render.com dashboard
    - https://devdojo.com/wave#demo
- [ ] forgot password flow
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
- [ ] web components
    - lit
    - shoelace
- [ ] dockerfile - https://inboard.bws.bio/?
- [ ] deploy docker to render
    - https://docs.render.com/docker

## references

- https://github.com/mjhea0/awesome-fastapi
- https://github.com/whythawk/full-stack-fastapi-postgresql/blob/master/docs/development-guide.md

tailwind

- https://github.com/themesberg/tailwind-flask-starter

ui elements

- https://devdojo.com/pines
