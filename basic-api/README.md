# basic-api

Saas platform api using

- fastapi
- htmx
- tailwindUI/Flowbite

todo:

- [x] deploy to render
- [x] add fastapi-users
- [x] transactional tests
- [x] add fastapi-users endpoint tests
- [x] cleanup app.py - split users into module/apirouter
- [x] add htmx
- [x] add styling - tailwind/flowbite
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
- [ ] db migrations
- [ ] crud users
- [ ] test coverage
- [ ] playwright
- [ ] csrf - https://github.com/simonw/asgi-csrf
- [ ] view profile
- [ ] app user management
    - click to edit forms: https://htmx.org/examples/click-to-edit/
    - dashboard: https://flowbite-admin-dashboard.vercel.app/layouts/stacked/
    - icons: https://github.com/sirvan3tr/jinja-primer-icons
    - example: render.com dashboard
    - https://devdojo.com/wave#demo
- [ ] forgot password flow
- [ ] mailapi - sendgrid?
    - https://sabuhish.github.io/fastapi-mail/example/
    - https://pramod4040.medium.com/fastapi-forget-password-api-setup-632ab90ba958
- [ ] dockerfile - https://inboard.bws.bio/?
- [ ] deploy docker to render
    - https://docs.render.com/docker
- [ ] cicd deployment pipeline
- [ ] branch deploys (preview environments)
- [ ] stripe integration
- [ ] webhooks
- [ ] queueing
- [ ] dependabot
- [ ] sentry
- [ ] codecov
- [ ] static files
    - https://docs.render.com/deploy-minio
    - run minio
      locally https://ktyptorio.medium.com/simple-openweather-api-service-using-fastapi-and-minio-object-storage-docker-version-f3587f7eb3de
- [ ] postgres rls
- [ ] multi tenant
- [ ] web components
    - lit
    - shoelace

refs:

- https://github.com/mjhea0/awesome-fastapi
- https://github.com/whythawk/full-stack-fastapi-postgresql/blob/master/docs/development-guide.md

tailwind
https://github.com/themesberg/tailwind-flask-starter

ui elements

- https://devdojo.com/pines
