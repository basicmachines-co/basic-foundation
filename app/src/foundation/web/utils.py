from typing import Optional

from fastapi import Request


# Utility to set flash message
def flash(request: Request, message: str):
    request.session["flash"] = message


# Utility to get and remove flash message
def get_flashed_message(request: Request) -> Optional[str]:
    message = request.session.pop("flash", None)
    return message
