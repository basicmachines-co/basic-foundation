from uuid import UUID

from fastapi import Request, Header, HTTPException
from fastapi import Response
from fastapi import status
from starlette.responses import HTMLResponse

from foundation.api.routes.users import update_user
from foundation.core.users.deps import UserServiceDep, UserPaginationDep
from foundation.core.users.models import User
from foundation.core.users.schemas import UserPublic
from foundation.core.users.services import (
    UserValueError,
    UserNotFoundError,
    UserCreateError,
)
from sqlalchemy import select, desc, asc
from starlette_wtf import csrf_token
from starlette_wtf.csrf import get_csrf_token

from foundation.web.deps import CurrentUserDep, LoginRequired, AdminRequired
from foundation.web.forms import UserEditForm, UserCreateForm
from foundation.web.templates import template, render
from foundation.web.utils import HTMLRouter, error_notification

router = HTMLRouter(dependencies=[LoginRequired])


def authorize_admin_or_owner(*, user: User, current_user: UserPublic):
    """
    Authorize admin or the owner of a resource.

    @param user: The user whose resource is being accessed
    @param current_user: The user making the request
    @return: Response with a 403 status if not authorized

    Error cases:
        - Returns a 403 Forbidden response if the current_user is neither an admin nor the user passed in.
    """
    if current_user.is_admin:
        return
    if user.id != current_user.id:
        return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.get("/users", dependencies=[AdminRequired])
async def users_page(request: Request, current_user: CurrentUserDep):
    """
    :param request: The incoming HTTP request.
    :param current_user: Dependency that holds information about the currently authenticated user.
    :return: Renders the users page with the current user's information.
    """
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
    """
    Handles listing of users with pagination and sorting options. This endpoint is secured by `AdminRequired`.

    :param request: The request object
    :param user_pagination: Dependency that provides pagination functionality
    :param current_user: Dependency that provides the current authenticated user
    :param page_num: The number of the page to retrieve, default is 1
    :param page_size: The number of items per page, default is 10
    :param order_by: Determines the field by which to order the results, default is "full_name"
    :param ascending: Boolean indicating order direction; True for ascending (default), False for descending
    :return: Rendered HTML template with the user list and pagination controls

    Example usage:
        GET /users/list?page_num=2&page_size=5&order_by=email&ascending=False
    Error Cases:
    - If `order_by` is not "full_name" or "email", it defaults to "full_name".
    HTMX Specific Behavior:
    - Returns a UserList component containing the paginated user list.
    """
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

    # Render the component and return it in response
    modal_component = render("user.UserList", current_user=current_user, page=page)
    return HTMLResponse(modal_component)


@router.get("/users/create", dependencies=[AdminRequired])
async def user_create(
    request: Request,
    current_user: CurrentUserDep,
):
    """
    Handles the user creation endpoint accessible only to admin users.
    :param request: FastAPI Request object.
    :param current_user: Dependency that provides the current authenticated user.
    :return: Rendered HTML template for creating a user.
    HTMX Specific Behavior:
    - Returns a template "pages/user_create.html" containing the user creation form.
    """
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
    """
    Handles user creation via a POST request. Validates the form input, creates a new user if validation passes,
    and redirects to the user detail view upon successful creation.

    :param request: The HTTP request object.
    :param user_service: Dependency for user service operations.
    :param current_user: Dependency for the current user.
    :return: Renders the user creation form with errors if validation fails, redirects to the user detail view
    if user creation is successful, or returns an error notification if user creation fails with UserCreateError.

    Error cases:
    - Form validation failure: Returns a template with HTTP 422 status code.
    - User creation failure: Returns an error notification rendered from an exception message.
    HTMX Specific Behavior:
    - If form validation fails, returns a UserCreate component with status 422.
    - On success, returns a response with status 307 to redirect to the user detail view.
    """
    form = await UserCreateForm.from_formdata(request)
    if not await form.validate():
        modal_component = render("user.UserCreate", form=form)
        return HTMLResponse(
            modal_component, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
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


@router.get("/users/{user_id}")
async def user_detail_view(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Retrieves details of a user by ID, checks if the current user is authorized as an admin or the owner,
    and renders an HTML page with the user's details.

    :param request: HTTP request object.
    :param user_id: ID of the user to retrieve.
    :param user_service: Dependency for accessing user services.
    :param current_user: Currently authenticated user.
    :return: Rendered HTML template for user detail view.

    Error cases:
    - Throws authorization error if current user is neither admin nor owner.
    HTMX Specific Behavior:
    - Returns a partial template "pages/user_view.html" displaying the user details.
    """
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
    """
    Fetch user details by ID, authorize the current user, and return an editable form for the user.

    :param request: The HTTP request object.
    :param user_id: The UUID of the user.
    :param user_service: Dependency that provides user service operations.
    :param current_user: Dependency that provides the current authenticated user.
    :return: Rendered HTML template with user details and edit form.
    :raises HTTPException: If the current user is not authorized to edit the user details.

    HTMX Specific Behavior:
    - Returns a partial template "partials/user/user_detail_edit.html" displaying the edit form for the user.
    """
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserEditForm(request, obj=edit_user)
    authorize_admin_or_owner(user=edit_user, current_user=current_user)

    modal_component = render(
        "user.UserDetailEdit", request=request, user=edit_user, form=form
    )
    return HTMLResponse(modal_component)


@router.put("/users/detail/{user_id}")
async def user_detail_put(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Updates the details of a user based on the provided form data.
    Accepts the user ID, request payload, and current user's information.
    Checks permissions and then validates and processes the form.
    Handles both regular users and admins differently based on permissions.
    Returns an error notification if there's an issue with the values provided.

    :param request: HTTP request object.
    :param user_id: UUID of the user to be updated.
    :param user_service: Service to handle business logic related to user management.
    :param current_user: Currently authenticated user performing the operation.
    :return: HTML template with updated user details or error notification.

    Error Cases:
    - Form validation failure: Returns a template with HTTP 422 status code.
    - User value error: Returns an error notification rendered from an exception message.
    HTMX Specific Behavior:
    - On form validation failure: Returns a partial template "partials/user/user_detail_edit.html" with status 422.
    - On successful update: Returns a partial template "partials/user/user_detail_view.html".
    """
    user = await user_service.get_user_by_id(user_id=user_id)
    form = await UserEditForm.from_formdata(request)
    authorize_admin_or_owner(user=user, current_user=current_user)
    if not await form.validate():
        # display the page with errors
        modal_component = render("user.UserDetailEdit", user=user, form=form)
        return HTMLResponse(
            modal_component, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    try:
        # if the user is not an admin, they can not set these fields
        if not current_user.is_admin:
            update_dict = {
                k: v for k, v in form.data.items() if k not in ("status", "role")
            }
        else:
            update_dict = form.data
        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict=update_dict,
        )
    except UserValueError as e:
        return error_notification(request, e.args[0])

    # show the detail view
    modal_component = render("user.UserDetailView", user=updated_user, hx_swap_oob=True)
    return HTMLResponse(modal_component)


@router.get("/users/modal/{user_id}/edit", dependencies=[AdminRequired])
async def user_modal_edit(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
):
    """
    Fetches user data for a given user ID and renders an editable user modal form.

    :param request: Current request object
    :param user_id: UUID of the user to be edited
    :param user_service: Dependency for user-related operations
    :return: Rendered template for user edit modal

    Error Cases:
    - If user ID does not exist, user_service.get_user_by_id may raise an exception.
    HTMX Specific Behavior:
    - Returns a partial template "pages/user_modal.html" with the user details and edit form.
    """
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    form = UserEditForm(request, obj=edit_user)

    # Render the component and return it in response
    modal_component = render(
        "user.UserModal", request=request, user=edit_user, form=form
    )
    return HTMLResponse(modal_component)


@router.put("/users/modal/{user_id}", dependencies=[AdminRequired])
async def user_modal_put(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
):
    """
    Handles PUT requests to update a user's data via a modal form. Validates the form and updates the user details.

    :param request: HTTP request object containing form data
    :param user_id: UUID of the user to update
    :param user_service: Dependency to interact with user data service
    :return: Renders a template with the updated user or form with errors

    Raises:
        UserValueError: If there is an issue with the user data during update.
    HTMX Specific Behavior:
    - On form validation failure: Returns a partial template "partials/user/user_modal_edit.html" with status 422.
    - On successful update: Returns a partial template "pages/user_modal.html" with close_modal flag and HX-Trigger refresh.
    """
    user = await user_service.get_user_by_id(user_id=user_id)
    form = await UserEditForm.from_formdata(request)
    if not await form.validate():
        # Render the component and return it in response with errors
        modal_component = render(
            "user.UserModal", request=request, user=user, form=form
        )
        return HTMLResponse(
            modal_component, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            update_dict=form.data,
        )
    except UserValueError as e:
        return error_notification(request, e.args[0])

    # Render the model as closed
    # return a trigger to refresh the user list
    modal_component = render(
        "user.UserModal",
        request=request,
        user=updated_user,
        form=form,
        close_modal=True,
    )
    return HTMLResponse(modal_component, headers={"HX-Trigger": "refresh"})


@router.get("/users/modal/{user_id}/delete", dependencies=[AdminRequired])
async def user_delete_modal_confirm(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
):
    """
    Handles a GET request to confirm deletion of a user. This requires admin privileges.

    :param request: The incoming HTTP request.
    :param user_id: The UUID of the user to be deleted.
    :param user_service: Dependency to interact with user-related operations.
    :param current_user: The current logged-in user's context.
    :return: Renders the user deletion confirmation modal template with relevant data.

    HTMX Specific Behavior:
    - Returns a UserModalDeleteConfirm confirming the user deletion.
    """
    user = await user_service.get_user_by_id(user_id=user_id)
    token = csrf_token(request)

    modal_component = render("user.UserModalDeleteConfirm", user=user, csrf_token=token)
    return HTMLResponse(modal_component)


@router.delete("/users/{user_id}", dependencies=[AdminRequired])
async def delete_user(
    request: Request,
    user_id: UUID,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
    x_csrftoken: str = Header(None),
):
    """
    Deletes a user by user_id if the current user has admin privileges. It also
    prevents a user from deleting their own account. CSRF token validation is
    required. Returns an HTTP 403 error if the CSRF token is invalid or the user
    attempts to delete their own account. Returns an HTTP 404 error if the user
    is not found.

    :param request: Current HTTP request.
    :param user_id: UUID of the user to delete.
    :param user_service: Dependency that provides user-related operations.
    :param current_user: Dependency that provides currently authenticated user's information.
    :param x_csrftoken: CSRF token from the header for validation.
    :return: HTTP response redirecting to users page or raises HTTP exceptions.
    :raises HTTPException: If CSRF token is invalid, user attempts to delete themselves, or user not found.

    HTMX Specific Behavior:
    - On successful deletion: Returns a response with status 307 to redirect to the users page.
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
