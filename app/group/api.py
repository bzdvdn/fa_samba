from typing import List

from fastapi import APIRouter, Depends, HTTPException

# from fastapi.exceptions import HTTPException
from app.core.constants import DEFAULT_SUCCESS_RESPONSE

from .schemas import (
    AddGroup,
    GroupUsersManage,
    GroupDetail,
)
from app.user.security import get_current_user
from .services import manager

api_router = APIRouter()


@api_router.post(
    "/add_group/",
    status_code=200,
)
async def add_group(
    add_group: AddGroup,
    current_user: dict = Depends(get_current_user),
):
    await manager.add_group(current_user, add_group)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/delete_group/",
    status_code=200,
)
async def delete_group(
    groupname: str,
    current_user: dict = Depends(get_current_user),
):
    await manager.delete_group(current_user, groupname)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/add_users_to_group/",
    status_code=200,
)
async def add_users_to_group(
    user_group_manage: GroupUsersManage,
    current_user: dict = Depends(get_current_user),
):
    await manager.add_users_to_group(current_user, user_group_manage)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/remove_users_from_group/",
    status_code=200,
)
async def remove_users_from_group(
    user_group_manage: GroupUsersManage,
    current_user: dict = Depends(get_current_user),
):
    await manager.remove_users_from_group(current_user, user_group_manage)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.get("/list/", status_code=200, response_model=List[GroupDetail])
async def list_groups(
    current_user: dict = Depends(get_current_user),
):
    return await manager.list_groups(current_user)


@api_router.get("/get/", status_code=200, response_model=GroupDetail)
async def get_group_by_name(
    name: str,
    current_user: dict = Depends(get_current_user),
):
    group = await manager.get_group_by_name(current_user, name)
    if group:
        return group
    raise HTTPException(404, f"group with name `{name}` does not exists.")


@api_router.get(
    "/users_by_group/",
    status_code=200,
)
async def list_users_by_group(
    groupname: str,
    current_user: dict = Depends(get_current_user),
):
    return await manager.list_users_by_group(current_user, groupname)
