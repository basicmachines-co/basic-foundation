from fastapi import APIRouter
from starlette import status
from starlette.responses import HTMLResponse

from modules.foundation.web.templates import template


class HTMLRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_in_schema = False
        self.default_response_class = HTMLResponse


def notification(request, message, title="OK!", status_code=status.HTTP_200_OK):
    return template(
        request,
        "partials/notification.html",
        {"title": title, "message": message},
        status_code=status_code,
        headers={"HX-Trigger": "notification"},
    )


def error_notification(
    request, message, title="An error occurred", status_code=status.HTTP_400_BAD_REQUEST
):
    return template(
        request,
        "partials/notification.html",
        {"error": True, "title": title, "message": message},
        status_code=status_code,
        headers={"HX-Trigger": "notification"},
    )
