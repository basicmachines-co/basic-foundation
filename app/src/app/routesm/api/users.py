from fastapi import Response, APIRouter
from fastapi import Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer

access_security = JwtAccessBearer(secret_key="secret_key", auto_error=True)

user_router = APIRouter()


@user_router.post("/auth")
def auth():
    subject = {"username": "username", "role": "user"}
    return {"access_token": access_security.create_access_token(subject=subject)}


@user_router.post("/auth_cookie")
def auth(response: Response):
    subject = {"username": "username", "role": "user"}
    access_token = access_security.create_access_token(subject=subject)
    access_security.set_access_cookie(response, access_token)
    return {"access_token": access_token}


@user_router.get("/users/me")
def read_current_user(
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    return {"username": credentials["username"], "role": credentials["role"]}
