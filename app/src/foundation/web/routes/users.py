from uuid import UUID

from fastapi import Request, Header, HTTPException
from fastapi import Response
from fastapi import status
from sqlalchemy import select, desc, asc
from starlette_wtf import csrf_token
from starlette_wtf.csrf import get_csrf_token

from foundation.users.deps import UserServiceDep, UserPaginationDep
from foundation.users.models import User
from foundation.users.schemas import UserPublic
from foundation.users.services import UserValueError, UserNotFoundError, UserCreateError
from foundation.web.deps import CurrentUserDep, LoginRequired, AdminRequired
from foundation.web.forms import UserEditForm, UserCreateForm
from foundation.web.templates import template
from foundation.web.utils import HTMLRouter, error_notification

router = HTMLRouter(dependencies=[LoginRequired])


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
    page_num: int = 1,
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

    pagination = user_pagination.paginate(
        request, query, page_size=page_size, order_by=order_by, asc=ascending
    )
    page = await pagination.page(page=page_num)
    return template(
        request,
        "partials/user/user_list.html",
        {"current_user": current_user, "page": page},
    )


@router.get("/users/create", dependencies=[AdminRequired])
async def user_create(
    request: Request,
    current_user: CurrentUserDep,
):
    form = UserCreateForm(request)
    return template(
        request,
        "pages/user_create.html",
        {"request": request, "current_user": current_user, "form": form},
    )


@router.post("/users/create", dependencies=[AdminRequired])
async def user_create_post(
    request: Request,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    form = await UserCreateForm.from_formdata(request)
    if await form.validate():
        try:
            created_user = await user_service.create_user(create_dict=form.data)
            # Because we are handling a post, we do a redirect in the response
            return Response(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={
                    "HX-Redirect": router.url_path_for(
                        "user_detail_view", user_id=created_user.id
                    )
                },
            )
        except UserCreateError as e:
            return error_notification(request, e.args[0])

    return template(
        request,
        "partials/user/user_form.html",
        {"current_user": current_user, "form": form},
    )


@router.get("/users/{user_id}")
async def user_detail_view(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    view_user = await user_service.get_user_by_id(user_id=user_id)
    authorize_admin_or_owner(user=view_user, current_user=current_user)
    return template(
        request,
        "pages/user_view.html",
        {"user": view_user, "current_user": current_user},
    )


@router.get("/users/detail/{user_id}/edit")
async def user_detail_edit(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserEditForm(request, obj=edit_user)
    authorize_admin_or_owner(user=edit_user, current_user=current_user)

    return template(
        request,
        "partials/user/user_detail_edit.html",
        {"user": edit_user, "form": form},
    )


@router.put("/users/detail/{user_id}")
async def user_detail_put(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    user = await user_service.get_user_by_id(user_id=user_id)
    form = await UserEditForm.from_formdata(request)
    authorize_admin_or_owner(user=user, current_user=current_user)

    if not await form.validate():
        # display the page with errors
        return template(
            request,
            "partials/user/user_detail_edit.html",
            {"user": {"id": user_id}, "form": form},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        # if the user is not an admin, they can not set these fields
        if not current_user.is_superuser:
            update_dict = {
                k: v
                for k, v in form.data.items()
                if k not in ("is_superuser", "is_active")
            }
        else:
            update_dict = form.data

        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict=update_dict,
        )
    except UserValueError as e:
        return error_notification(request, e.args[0])

    return template(
        request,
        "partials/user/user_detail_view.html",
        {"user": updated_user, "form": form, "hx_swap_oob": True},
    )


@router.get("/users/modal/{user_id}/edit", dependencies=[AdminRequired])
async def user_modal_edit(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserEditForm(request, obj=edit_user)
    return template(request, "pages/user_modal.html", {"user": edit_user, "form": form})


@router.put("/users/modal/{user_id}", dependencies=[AdminRequired])
async def user_modal_put(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
):
    user = await user_service.get_user_by_id(user_id=user_id)
    form = await UserEditForm.from_formdata(request)
    if not await form.validate():
        # display the form with errors
        return template(
            request,
            "partials/user/user_modal_edit.html",
            {"user": user, "form": form},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict=form.data,
        )
    except UserValueError as e:
        return error_notification(request, e.args[0])

    return template(
        request,
        "pages/user_modal.html",
        {"user": updated_user, "form": form, "close_modal": True},
        headers={"HX-Trigger": "refresh"},
    )


@router.get("/users/modal/{user_id}/delete", dependencies=[AdminRequired])
async def user_modal_delete(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    user = await user_service.get_user_by_id(user_id=user_id)
    token = csrf_token(request)

    return template(
        request,
        "partials/user/user_modal_delete.html",
        {"user": user, "current_user": current_user, "csrf_token": token},
    )


@router.delete("/users/{user_id}", dependencies=[AdminRequired])
async def delete_user(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
    x_csrftoken: str = Header(None),
):
    """
    Delete a user
    """
    if user_id == current_user.id:
        return error_notification(
            request, "You can't delete yourself", status_code=status.HTTP_403_FORBIDDEN
        )

    # Validate the CSRF token from the header
    if x_csrftoken is None or x_csrftoken != await get_csrf_token(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
        )

    try:
        await user_service.get_user_by_id(user_id=user_id)
        await user_service.delete_user(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])

    response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.headers["HX-Redirect"] = router.url_path_for("users_page")
    return response
