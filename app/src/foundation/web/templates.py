from jinja2 import pass_context
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks

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
