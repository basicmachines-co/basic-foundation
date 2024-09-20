from fastapi import Request
from starlette.responses import RedirectResponse

from foundation.users.deps import UserServiceDep
from foundation.web.deps import CurrentUserDep, LoginRequired, AdminRequired
from foundation.web.templates import templates
from foundation.web.utils import HTMLRouter

router = HTMLRouter()


@router.get("/")
async def index(
    current_user: CurrentUserDep,
):
    if current_user.is_superuser:
        return RedirectResponse(url=router.url_path_for("dashboard"))
    else:
        return RedirectResponse(url=router.url_path_for("profile"))


@router.get("/dashboard", dependencies=[AdminRequired])
async def dashboard(
    request: Request,
    current_user: CurrentUserDep,
):
    return templates.TemplateResponse(
        "pages/dashboard.html",
        dict(
            request=request,
            current_user=current_user,
        ),
    )


@router.get("/dashboard/users/count", dependencies=[AdminRequired])
async def dashboard_users_count(request: Request, user_service: UserServiceDep):
    users_count = await user_service.get_users_count()
    return templates.TemplateResponse(
        "partials/stat.html",
        {"request": request, "name": "Total Users", "value": users_count},
    )


@router.get("/dashboard/users/active_count", dependencies=[AdminRequired])
async def dashboard_active_users_count(request: Request, user_service: UserServiceDep):
    count = await user_service.get_active_users_count()
    return templates.TemplateResponse(
        "partials/stat.html",
        {"request": request, "name": "Active Users", "value": count},
    )


@router.get("/dashboard/users/admin_count", dependencies=[AdminRequired])
async def dashboard_admin_users_count(request: Request, user_service: UserServiceDep):
    count = await user_service.get_admin_users_count()
    return templates.TemplateResponse(
        "partials/stat.html",
        {"request": request, "name": "Admin Users", "value": count},
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
