from dataclasses import dataclass, field
from typing import Dict, Any

from jinja2 import pass_context
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks
from starlette.requests import Request

from foundation.core.config import BASE_DIR

templates = Jinja2Blocks(
    directory=f"{BASE_DIR}/templates",
)
templates.env.add_extension(DebugExtension)


class FlashMessageJinja(Jinja2Blocks):
    def _create_env(self, *args, **kwargs):
        env = super()._create_env(*args, **kwargs)
        env.globals["get_flashed_message"] = self.get_flashed_message
        return env

    @pass_context
    def get_flashed_message(self, context):
        request = context["request"]
        message = request.session.pop("flash", None)
        return message


# Set up Jinja2 templates with the custom class
templates = FlashMessageJinja(directory="templates")


@dataclass
class TemplateContext:
    request: Request
    _data: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        if not isinstance(self.request, Request):
            raise TypeError("The 'request' property must be of type 'Request'.")

    def __getitem__(self, key: str) -> Any:
        if key == "request":
            return self.request
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "request":
            self.request = value
        else:
            self._data[key] = value

    def __delitem__(self, key: str) -> None:
        if key == "request":
            raise KeyError("Cannot delete the 'request' property.")
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        if key == "request":
            return True
        return key in self._data

    def keys(self):
        return ["request"] + list(self._data.keys())

    def items(self):
        return [("request", self.request)] + list(self._data.items())

    def get(self, key: str, default: Any = None) -> Any:
        if key == "request":
            return self.request
        return self._data.get(key, default)

    def __repr__(self) -> str:
        return f"TemplateContext(request={self.request}, data={self._data})"
