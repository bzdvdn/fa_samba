from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# from fastapi.exceptions import HTTPException

from app.core.constants import DEFAULT_SUCCESS_RESPONSE

from .schemas import (
    AuthUser,
    TokenData,
    AddUser,
    UpdateUserPassword,
    UserList,
    MoveUserOU,
    UpdateTokensSchema,
    UserRow,
)
from .security import auth_scheme, get_current_user
from .services import manager


api_router = APIRouter()


@api_router.post(
    "/token_auth/",
    response_model=TokenData,
    status_code=201,
)
async def login_for_access_token(auth_data: AuthUser):
    return await manager.auth(auth_data.username, auth_data.password)


@api_router.post(
    "/refresh_token/",
    response_model=TokenData,
)
async def update_tokens(data: UpdateTokensSchema):
    return await manager.update_tokens(data.refresh_token)


@api_router.get(
    "/me/",
)
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return await manager.get_me(credentials)


@api_router.get(
    "/list_users/",
    response_model=UserList,
)
async def list_users(current_user: dict = Depends(get_current_user)):
    return await manager.get_users(current_user)


@api_router.get(
    "/get/",
    response_model=UserRow,
)
async def get_user_by_username(
    username: str, current_user: dict = Depends(get_current_user)
):
    user = await manager.get_user_by_username(current_user, username)
    if not user:
        raise HTTPException(404, f"user with `{username}` does not exists.")
    return user


@api_router.post(
    "/create_user/",
)
async def create_user(
    add_user: AddUser, current_user: dict = Depends(get_current_user)
):
    await manager.create_user(current_user, add_user=add_user)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/delete_user/",
    status_code=200,
)
async def delete_user(username: str, current_user: dict = Depends(get_current_user)):
    await manager.delete_user(current_user, username)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/update_password/",
    status_code=200,
)
async def update_user_password(
    update_user_password: UpdateUserPassword,
    current_user: dict = Depends(get_current_user),
):
    await manager.update_user_password(current_user, update_user_password)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/move_user_ou/",
    status_code=200,
)
async def move_user_organization(
    move: MoveUserOU,
    current_user: dict = Depends(get_current_user),
):
    await manager.move_user_ou(current_user, move)
    return DEFAULT_SUCCESS_RESPONSE
