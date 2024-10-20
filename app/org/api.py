from typing import List

from fastapi import APIRouter, Depends

# from fastapi.exceptions import HTTPException

from app.core.constants import DEFAULT_SUCCESS_RESPONSE
from app.user.security import get_current_user

from .schemas import (
    AddOrganizationUnit,
    SearchByOU,
    SearchOURow,
)
from .services import manager

api_router = APIRouter()


@api_router.post(
    "/add_ou/",
    status_code=200,
)
async def add_organization_unit(
    add_org_unit: AddOrganizationUnit,
    current_user: dict = Depends(get_current_user),
):
    await manager.create_organization_unit(current_user, add_org_unit)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/delete_ou/",
    status_code=200,
)
async def delete_organization(
    ou_dn: str,
    current_user: dict = Depends(get_current_user),
):
    await manager.delete_organization(current_user, ou_dn)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.post(
    "/search/",
    status_code=200,
    response_model=List[SearchOURow],
)
async def search_by_ou(
    search_by_ou: SearchByOU,
    current_user: dict = Depends(get_current_user),
):
    res = await manager.search_by_ou(
        current_user,
        search_by_ou.ou,
        search_by_ou.object_classes,
        attrs=search_by_ou.attrs,
    )
    return res
