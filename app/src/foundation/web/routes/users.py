from uuid import UUID

from fastapi import Request, Form, Response, APIRouter
from fastapi import status
from sqlalchemy import select
from starlette.responses import HTMLResponse

from foundation.users.deps import UserServiceDep, UserPaginationDep
from foundation.users.models import User
from foundation.users.schemas import Message
from foundation.users.services import UserValueError, UserNotFoundError
from foundation.web.deps import CurrentUserDep
from foundation.web.templates import templates
from foundation.web.utils import flash

router = APIRouter(include_in_schema=False, default_response_class=HTMLResponse)


@router.get("/users")
async def users(
        request: Request,
        user_pagination: UserPaginationDep,
        current_user: CurrentUserDep,
        page: int = 1,
        page_size: int = 10,
):
    query = select(User)
    pagination = user_pagination.paginate(request, query, page_size=page_size)
    page = await pagination.page(page=page)

    return templates.TemplateResponse(
        "pages/user_list.html",
        {
            "request": request,
            "page": page,
        },
    )


@router.get("/users/create")
async def user_create(
        request: Request,
        current_user: CurrentUserDep,
):
    return templates.TemplateResponse(
        "pages/user_create.html",
        {"request": request, "current_user": current_user, "user": None},
    )


@router.post("/users/create")
async def user_create_post(
        request: Request,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
        full_name: str = Form(),
        email: str = Form(),
        password: str = Form(),
        is_active: bool = Form(False),
        is_superuser: bool = Form(False),
):
    error = None
    try:
        created_user = await user_service.create_user(
            create_dict={
                "full_name": full_name,
                "email": email,
                "password": password,
                "is_active": is_active,
                "is_superuser": is_superuser,
            }
        )
    except UserValueError as e:
        error = e.args
        return templates.TemplateResponse(
            "pages/user_create.html",
            {
                "request": request,
                "error": error,
                "user": {
                    "full_name": full_name,
                    "email": email,
                    "is_active": is_active,
                    "is_superuser": is_superuser,
                },
            },
            block_name="content",
        )

    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "error": error, "user": created_user},
        block_name="content",
    )


@router.get("/users/{user_id}")
async def user(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    view_user = await user_service.get_user_by_id(user_id=user_id)
    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "current_user": current_user, "user": view_user},
    )


@router.get("/users/{user_id}/edit")
async def user_edit(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    return templates.TemplateResponse(
        "pages/user_edit.html",
        {"request": request, "current_user": current_user, "user": edit_user},
        block_name="content",
    )


@router.post("/users/{user_id}")
async def user_edit_post(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
        full_name: str = Form(),
        email: str = Form(),
        is_active: bool = Form(False),
        is_superuser: bool = Form(False),
):
    error = None
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict={
                "full_name": full_name,
                "email": email,
                "is_active": is_active,
                "is_superuser": is_superuser,
            },
        )
    except UserValueError as e:
        error = e.args
        return templates.TemplateResponse(
            "pages/user_edit.html",
            {
                "request": request,
                "error": error,
                "user": {
                    "full_name": full_name,
                    "email": email,
                    "is_active": is_active,
                    "is_superuser": is_superuser,
                },
            },
            block_name="content",
        )

    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "error": error, "user": updated_user},
        block_name="content",
    )


@router.delete("/users/{user_id}")
async def delete_user(
        request: Request,
        user_service: UserServiceDep,
        user_id: UUID,
        current_user: CurrentUserDep,
):
    """
    Delete a user.
    If the current_user is a non-super user, they can only delete their own user.
    Superusers can delete any other user.
    Superusers can not delete their own user.
    """
    if not current_user.is_superuser:
        return Message(message="Only admins can delete users.")

    try:
        user = await user_service.get_user_by_id(user_id=user_id)
        await user_service.delete_user(user_id=user_id)
    except UserNotFoundError as e:
        return Message(message=e.args[0])

    flash(request, f"User {user.full_name} was deleted")
    response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.headers["HX-Redirect"] = router.url_path_for("users")
    return response
