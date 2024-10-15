from fastapi import APIRouter
from starlette import status
from starlette.responses import HTMLResponse

from foundation.web.templates import render


class HTMLRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_in_schema = False
        self.default_response_class = HTMLResponse


def notification(request, message, title="OK!", status_code=status.HTTP_200_OK):
    component = render("Notification", title=title, message=message)
    return HTMLResponse(
        component, status_code=status_code, headers={"HX-Trigger": "notification"}
    )


def error_notification(
    request, message, title="An error occurred", status_code=status.HTTP_400_BAD_REQUEST
):
    component = render("Notification", error=True, title=title, message=message)
    return HTMLResponse(
        component, status_code=status_code, headers={"HX-Trigger": "notification"}
    )
