from uuid import UUID

from fastapi import Request, APIRouter, Response
from sqlalchemy import select
from starlette.responses import HTMLResponse

from foundation.users.deps import UserServiceDep, UserPaginationDep
from foundation.users.models import User
from foundation.users.services import UserValueError, UserNotFoundError
from foundation.web.deps import CurrentUserDep
from foundation.web.forms import UserCreateForm, UserEditForm
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
        dict(
            request=request,
            page=page,
        ),
    )


@router.get("/users/create")
async def user_create(
        request: Request,
):
    form = UserCreateForm(request)
    return templates.TemplateResponse(
        "pages/user_create.html",
        dict(
            request=request,
            form=form
        ),
    )


@router.post("/users/create")
async def user_create_post(
        request: Request,
        user_service: UserServiceDep,
):
    form = await UserCreateForm.from_formdata(request)
    error = None
    if await form.validate():
        try:
            created_user = await user_service.create_user(
                create_dict=form.data
            )
            return templates.TemplateResponse(
                "pages/user_view.html",
                dict(
                    request=request,
                    user=created_user
                ),
                block_name="content",
            )
        except UserValueError as e:
            error = e.args
    return templates.TemplateResponse(
        "pages/user_create.html",
        dict(
            request=request,
            error=error,
            form=form
        ),
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
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserEditForm(request, obj=edit_user)

    # Generate a CSRF token and set it in a cookie
    token = csrf_token(request)
    response = templates.TemplateResponse(
        "pages/user_edit.html",
        dict(
            request=request,
            user=edit_user,
            form=form
        ),
        block_name="content",
    )
    response.set_cookie("csrf_token", token)  # Set the CSRF token in the cookie
    return response


@router.post("/users/{user_id}")
async def user_edit_post(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    form = await UserEditForm.from_formdata(request)
    error = None

    edit_user = await user_service.get_user_by_id(user_id=user_id)
    if await form.validate():
        try:
            updated_user = await user_service.update_user(
                user_id=user_id,
                update_dict=form.data,
            )
            return templates.TemplateResponse(
                "pages/user_view.html",
                dict(
                    request=request,
                    user=updated_user
                ),
                block_name="content",
            )
        except UserValueError as e:
            error = e.args

    return templates.TemplateResponse(
        "pages/user_edit.html",
        dict(
            request=request,
            user=edit_user,
            error=error,
            form=form
        ),
        block_name="content",
    )


from fastapi import Request, Header, HTTPException
from fastapi import status
from starlette_wtf import csrf_token


@router.delete("/users/{user_id}")
async def delete_user(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
        x_csrftoken: str = Header(None)
):
    """
    Delete a user. Only admins can delete users.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete users.")

    # Retrieve the CSRF token from the cookie
    csrf_token_in_cookie = request.cookies.get("csrf_token")

    # Validate the CSRF token directly from the header
    if not x_csrftoken or x_csrftoken != csrf_token_in_cookie:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token.")

    try:
        user = await user_service.get_user_by_id(user_id=user_id)
        await user_service.delete_user(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])

    flash(request, f"User {user.full_name} was deleted")
    response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.headers["HX-Redirect"] = router.url_path_for("users")
    return response
