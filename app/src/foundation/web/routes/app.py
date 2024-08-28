from fastapi import Request
from starlette.responses import RedirectResponse

from foundation.users.deps import UserServiceDep
from foundation.web.deps import CurrentUserDep, LoginRequired
from foundation.web.templates import templates
from foundation.web.utils import HTMLRouter

router = HTMLRouter()


@router.get("/")
async def index():
    return RedirectResponse(url=router.url_path_for("dashboard"))


@router.get("/dashboard", dependencies=[LoginRequired])
async def dashboard(
        request: Request,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    return templates.TemplateResponse(
        "pages/dashboard.html",
        dict(
            request=request,
            current_user=current_user,
            users_count=await user_service.get_users_count(),
            active_users_count=await user_service.get_active_users_count(),
            admin_users_count=await user_service.get_admin_users_count(),
        ),
    )


@router.get("/profile", dependencies=[LoginRequired])
async def profile(
        request: Request,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    return templates.TemplateResponse(
        "pages/user_view.html",
        dict(
            request=request,
            current_user=current_user,
            user=await user_service.get_user_by_id(user_id=current_user.id),
        ),
    )
