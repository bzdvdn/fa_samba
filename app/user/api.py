from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

# from fastapi.exceptions import HTTPException

from .schemas import (
    AuthUser,
    TokenData,
    AddUser,
    UpdateUserPassword,
    UserList,
    AddOrganizationUnit,
    MoveUserOU,
    AddGroup,
    UserGroupManage,
)
from .security import auth_scheme
from .services import manager


api_router = APIRouter()

DEFAULT_SUCCESS_RESPONSE = {"message": "success"}


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
    await manager.create_user(credentials, add_user=add_user)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/create_user/",
    status_code=200,
)
async def delete_user(
    username: str, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    await manager.delete_user(credentials, username)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/update_password/",
    status_code=200,
)
async def update_user_password(
    update_user_password: UpdateUserPassword,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.update_user_password(credentials, update_user_password)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/add_ou/",
    status_code=200,
)
async def move_user_organization(
    add_org_unit: AddOrganizationUnit,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.create_organization_unit(credentials, add_org_unit)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/move_user_ou/",
    status_code=200,
)
async def create_organization_unit(
    move: MoveUserOU,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.move_user_ou(credentials, move)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/delete_organization/",
    status_code=200,
)
async def delete_organization(
    ou_dn: str,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.delete_organization(credentials, ou_dn)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/add_group/",
    status_code=200,
)
async def add_group(
    add_group: AddGroup,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.add_group(credentials, add_group)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/delete_group/",
    status_code=200,
)
async def delete_group(
    groupname: str,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.delete_group(credentials, groupname)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/add_users_to_group/",
    status_code=200,
)
async def add_users_to_group(
    user_group_manage: UserGroupManage,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.add_users_to_group(credentials, user_group_manage)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/remove_users_from_group/",
    status_code=200,
)
async def remove_users_from_group(
    user_group_manage: UserGroupManage,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    await manager.remove_users_from_group(credentials, user_group_manage)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.get(
    "/groups/",
    status_code=200,
)
async def list_groups(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    return await manager.list_groups(credentials)


@api_router.get(
    "/users_by_group/",
    status_code=200,
)
async def list_users_by_group(
    groupname: str,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    return await manager.list_users_by_group(credentials, groupname)
