from jinja2.ext import DebugExtension
from starlette.templating import Jinja2Templates

from foundation.core.config import BASE_DIR

templates = Jinja2Templates(directory=f"{BASE_DIR}/templates")
templates.env.add_extension(DebugExtension)
