
from .app import router as app_router
from .auth import router as auth_router
from .users import router as users_router
from ..utils import HTMLRouter

html_router = HTMLRouter()

# Include the routes from different modules
html_router.include_router(app_router, tags=["App"])
html_router.include_router(auth_router, tags=["Auth"])
html_router.include_router(users_router,  tags=["Users"])
