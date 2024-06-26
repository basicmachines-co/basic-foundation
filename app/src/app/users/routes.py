from app.users.deps import fastapi_users, jwt_backend
from app.users.schemas import UserRead, UserCreate, UserUpdate
from fastapi import APIRouter

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

auth_router.include_router(fastapi_users.get_auth_router(jwt_backend), prefix="/jwt")
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

user_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
