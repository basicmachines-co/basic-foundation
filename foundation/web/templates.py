import typing

import jinjax
from jinja2.ext import DebugExtension
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from foundation.core.config import BASE_DIR

templates = Jinja2Templates(directory=f"{BASE_DIR}/web/templates")
templates.env.add_extension(DebugExtension)

templates.env.add_extension(jinjax.JinjaX)  # pyright: ignore [reportPrivateImportUsage]
catalog = jinjax.Catalog(jinja_env=templates.env)  # pyright: ignore [reportPrivateImportUsage]
catalog.add_folder(f"{BASE_DIR}/web/components")
catalog.add_folder(f"{BASE_DIR}/web/layouts")


def template(
    request: Request,
    name: str,
    context: dict,
    status_code: int = 200,
    headers: typing.Optional[typing.Mapping[str, str]] = None,
    **kwargs,
) -> templates.TemplateResponse:  # pyright: ignore [reportInvalidTypeForm]
    return templates.TemplateResponse(
        request, name, context, status_code, headers, **kwargs
    )


def render(
    name: str,
    **kwargs,
) -> str:
    return catalog.render(name, **kwargs)
