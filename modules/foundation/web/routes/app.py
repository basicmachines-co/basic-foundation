from fastapi import Request
from starlette.responses import RedirectResponse

from foundation.users.deps import UserServiceDep
from modules.foundation.web.deps import CurrentUserDep, LoginRequired, AdminRequired
from modules.foundation.web.templates import templates
from modules.foundation.web.utils import HTMLRouter

router = HTMLRouter()


@router.get("/")
async def index(
    current_user: CurrentUserDep,
):
    """
    :param current_user: Dependency that represents the current authenticated user, expected to have an `is_admin` attribute.
    :return: Redirects to admin dashboard if the user is admin, otherwise redirects to user profile.
    """
    if current_user.is_admin:
        return RedirectResponse(url=router.url_path_for("dashboard"))
    else:
        return RedirectResponse(url=router.url_path_for("profile"))


@router.get("/dashboard", dependencies=[AdminRequired])
async def dashboard(
    request: Request,
    current_user: CurrentUserDep,
):
    """
    Fetches and renders the dashboard page for the current user if they are an admin.

    :param request: The incoming HTTP request object.
    :param current_user: The current authenticated user object.
    :return: Renders the 'dashboard.html' template with provided request and current user context.
    """
    return templates.TemplateResponse(
        "pages/dashboard.html",
        dict(
            request=request,
            current_user=current_user,
        ),
    )


@router.get("/dashboard/users/count", dependencies=[AdminRequired])
async def dashboard_users_count(request: Request, user_service: UserServiceDep):
    """
    :param request: The request object containing the HTTP request data
    :param user_service: A dependency injected service for user-related operations
    :return: A TemplateResponse object with user count statistics

    Asynchronously retrieves the total number of users from the user service.
    Renders the `partials/stat.html` template with the user count data.
    """
    users_count = await user_service.get_users_count()
    return templates.TemplateResponse(
        "partials/stat.html",
        {
            "request": request,
            "name": "Total Users",
            "id": "user-count",
            "value": users_count,
        },
    )


@router.get("/dashboard/users/active_count", dependencies=[AdminRequired])
async def dashboard_active_users_count(request: Request, user_service: UserServiceDep):
    """
    Retrieve and display the count of active users on the dashboard.

    :param request: The HTTP request object
    :param user_service: The user service dependency for fetching user data
    :return: Rendered template for the active user count section

    Example usage:
        @router.get("/dashboard/users/active_count", dependencies=[AdminRequired])
        async def dashboard_active_users_count(request: Request, user_service: UserServiceDep)
    """
    count = await user_service.get_active_users_count()
    return templates.TemplateResponse(
        "partials/stat.html",
        {
            "request": request,
            "name": "Active Users",
            "id": "active-user-count",
            "value": count,
        },
    )


@router.get("/dashboard/users/admin_count", dependencies=[AdminRequired])
async def dashboard_admin_users_count(request: Request, user_service: UserServiceDep):
    """
    :param request: FastAPI Request object
    :param user_service: Dependency for UserService
    :return: Rendered template with admin users count

    Retrieve the count of admin users using `user_service` and render an HTML fragment displaying this count.
    """
    count = await user_service.get_admin_users_count()
    return templates.TemplateResponse(
        "partials/stat.html",
        {
            "request": request,
            "name": "Admin Users",
            "id": "admin-user-count",
            "value": count,
        },
    )


@router.get("/profile", dependencies=[LoginRequired])
async def profile(
    request: Request,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Handles the GET request for the user profile page

    :param request: HTTP Request object, provides request metadata
    :param user_service: UserServiceDep instance, used to fetch user data
    :param current_user: CurrentUserDep instance, represents the logged-in user
    :return: HTTP response with the rendered user profile template
    """
    return templates.TemplateResponse(
        "pages/user_view.html",
        dict(
            request=request,
            current_user=current_user,
            user=await user_service.get_user_by_id(user_id=current_user.id),
        ),
    )
