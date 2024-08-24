from typing import Optional

from fastapi import Request, APIRouter
from starlette.responses import HTMLResponse


class HTMLRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_in_schema = False
        self.default_response_class = HTMLResponse


# Utility to set flash message
def flash(request: Request, message: str):
    request.session["flash"] = message


# Utility to get and remove flash message
def get_flashed_message(request: Request) -> Optional[str]:
    message = request.session.pop("flash", None)
    return message
