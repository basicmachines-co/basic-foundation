import typing
from uuid import UUID

from fastapi import Request, Header, HTTPException
from fastapi import Response
from fastapi import status
from sqlalchemy import select, desc, asc
from starlette_wtf import csrf_token

from foundation.users.deps import UserServiceDep, UserPaginationDep
from foundation.users.models import User
from foundation.users.schemas import UserPublic
from foundation.users.services import UserValueError, UserNotFoundError, UserCreateError
from foundation.web.deps import CurrentUserDep, LoginRequired, AdminRequired
from foundation.web.forms import UserForm
from foundation.web.templates import templates
from foundation.web.utils import flash, HTMLRouter

router = HTMLRouter(dependencies=[LoginRequired])


# helper methods to return template responses


def user_view_template(
        request: Request,
        user: User,
        *,
        current_user: UserPublic,
        block_name=None
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        "pages/user_view.html",
        dict(
            request=request,
            current_user=current_user,
            user=user
        ),
        block_name=block_name
    )


def user_create_template(
        request: Request,
        *,
        current_user: UserPublic,
        form: UserForm,
        error: str = None,
        block_name=None
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        "pages/user_create.html",
        dict(
            request=request,
            current_user=current_user,
            form=form,
            error=error,
        ),
        block_name=block_name,
    )


def partial_template(
        request: Request,
        user: dict = None,
        *,
        partial_template,
        form: UserForm = None,
        error: str = None,
        status_code=status.HTTP_200_OK,
        block_name=None,
        headers=None,
        **kwargs
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        f"partials/{partial_template}",
        dict(
            request=request,
            user=user,
            form=form,
            error=error,
            **kwargs
        ),
        status_code,
        headers=headers,
        block_name=block_name,
    )


def template(request: Request,
             name: str,
             context: dict,
             status_code: int = 200,
             headers: typing.Optional[typing.Mapping[str, str]] = None, **kwargs) -> templates.TemplateResponse:
    return templates.TemplateResponse(request, name, context, status_code, headers, **kwargs)


def authorize_admin_or_owner(*, user: User, current_user: UserPublic):
    if current_user.is_superuser:
        return
    if user.id != current_user.id:
        return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.get("/users", dependencies=[AdminRequired])
async def users_page(request: Request, current_user: CurrentUserDep):
    return template(request, "pages/users.html", {"current_user": current_user})


@router.get("/users/list", dependencies=[AdminRequired])
async def users_list(
        request: Request,
        user_pagination: UserPaginationDep,
        current_user: CurrentUserDep,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "full_name",
        ascending: bool = True,
):
    if order_by not in ["full_name", "email"]:
        order_by = "full_name"

    query = select(User)

    if ascending:
        query = query.order_by(asc(getattr(User, order_by)))
    else:
        query = query.order_by(desc(getattr(User, order_by)))

    pagination = user_pagination.paginate(request, query, page_size=page_size, order_by=order_by, asc=ascending)
    page = await pagination.page(page=page)
    return template(request, "partials/user/user_list.html", {"current_user": current_user, "page": page})


@router.get("/users/create",
            dependencies=[AdminRequired])
async def user_create(
        request: Request,
        current_user: CurrentUserDep,
):
    form = UserForm(request)
    return template(request, "pages/user_create.html", {"request": request, "current_user": current_user, "form": form})


@router.post("/users/create",
             dependencies=[AdminRequired])
async def user_create_post(
        request: Request,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    form = await UserForm.from_formdata(request)
    if await form.validate():
        try:
            created_user = await user_service.create_user(
                create_dict=form.data
            )
            # Because we are handling a post, we do a redirect in the response
            response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            response.headers["HX-Redirect"] = router.url_path_for("user_detail_view", user_id=created_user.id)
            return response
        except UserCreateError as e:
            pass
            # TODO return error
            # error = e.args[0]

    return template(request, "partials/user/user_form.html",
                    {"current_user": current_user, "form": form})


@router.get("/users/{user_id}")
async def user_detail_view(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    view_user = await user_service.get_user_by_id(user_id=user_id)
    authorize_admin_or_owner(user=view_user, current_user=current_user)
    return user_view_template(request, view_user, current_user=current_user)


@router.get("/users/detail/{user_id}/edit")
async def user_detail_edit(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserForm(request, obj=edit_user)
    authorize_admin_or_owner(user=edit_user, current_user=current_user)

    response = template(request, "partials/user/user_detail_edit.html", {"user": edit_user, "form": form})
    # Generate a CSRF token and set it in a cookie, checked on delete
    response.set_cookie("csrf_token", csrf_token(request))
    return response


@router.put("/users/detail/{user_id}")
async def user_detail_put(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    user = await user_service.get_user_by_id(user_id=user_id)
    form = await UserForm.from_formdata(request)
    authorize_admin_or_owner(user=user, current_user=current_user)

    if not await form.validate():
        # display the form with errors
        return template(request,
                        "partials/user/user_detail_edit.html",
                        {"user": {"id": user_id}, "form": form},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    try:
        # if the user is not an admin, they can not set these fields
        if not current_user.is_superuser:
            update_dict = {k: v for k, v in form.data.items() if k not in ('is_superuser', 'is_active')}
        else:
            update_dict = form.data

        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict=update_dict,
        )
        flash(request, f"User {updated_user.full_name} updated")
        return template(request,
                        "partials/user/user_detail_view.html",
                        {"user": updated_user, "form": form})
    except UserValueError as e:
        return partial_template(request,
                                user={"id": user_id},
                                form=form,
                                error=e.args[0],
                                partial_template="user/user_edit_error.html",
                                status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/users/modal/{user_id}/edit",
            dependencies=[AdminRequired])
async def user_modal_edit(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserForm(request, obj=edit_user)
    return template(request, "pages/user_modal.html", {"user": edit_user, "form": form})


@router.put("/users/modal/{user_id}",
            dependencies=[AdminRequired])
async def user_modal_put(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
):
    user = await user_service.get_user_by_id(user_id=user_id)
    form = await UserForm.from_formdata(request)
    if not await form.validate():
        # display the form with errors
        return template(request,
                        "partials/user/user_modal_edit.html",
                        {"user": user, "form": form},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict=form.data,
        )
    except UserValueError as e:
        # display an error notice
        return partial_template(request,
                                user={"id": user_id},
                                form=form,
                                error=e.args[0],
                                partial_template="user/user_modal_edit.html",
                                status_code=status.HTTP_400_BAD_REQUEST,
                                block_name="modal_content")

    flash(request, f"User {user.full_name} updated")
    return template(request,
                    "pages/user_modal.html",
                    {
                        "user": updated_user,
                        "form": form,
                        "close_modal": True},
                    headers={"HX-Trigger": "refresh"})


@router.delete("/users/{user_id}",
               dependencies=[AdminRequired])
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
    if not user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins can not delete their own user")

    # Retrieve the CSRF token from the cookie
    csrf_token_in_cookie = request.cookies.get("csrf_token")

    # Validate the CSRF token directly from the header
    if not x_csrftoken or x_csrftoken != csrf_token_in_cookie:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")

    try:
        user = await user_service.get_user_by_id(user_id=user_id)
        await user_service.delete_user(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])

    flash(request, f"User {user.full_name} was deleted")
    response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.headers["HX-Redirect"] = router.url_path_for("user_list")
    return response
