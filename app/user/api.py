from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

# from fastapi.exceptions import HTTPException

from .schemas import (
    AuthUser,
    TokenData,
    AddUser,
    UpdateUserPassword,
    UserList,
)
from .security import auth_scheme
from .services import manager


api_router = APIRouter()


@api_router.post(
    "/token_auth/",
    response_model=TokenData,
    status_code=201,
)
async def login_for_access_token(auth_data: AuthUser):
    return await manager.auth(auth_data.username, auth_data.password)


@api_router.get(
    "/me/",
)
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return await manager.get_me(credentials)


@api_router.get(
    "/list_users/",
    response_model=UserList,
)
async def list_users(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return await manager.get_users(credentials)


@api_router.post(
    "/create_user/",
)
async def create_user(
    add_user: AddUser, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return await manager.create_user(credentials, add_user=add_user)


@api_router.delete(
    "/create_user/",
    status_code=200,
)
async def delete_user(
    username: str, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    await manager.delete_user(credentials, username)


@api_router.post(
    "/update_password/",
    status_code=200,
)
async def update_user_password(
    update_user_password: UpdateUserPassword,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.update_user_password(credentials, update_user_password)
