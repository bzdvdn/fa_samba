from typing import List

from fastapi import APIRouter, Depends

# from fastapi.exceptions import HTTPException

from app.core.constants import DEFAULT_SUCCESS_RESPONSE
from app.user.security import get_current_user

from .schemas import AddOrganizationUnit, OrgDetail
from .services import manager

api_router = APIRouter()


@api_router.post(
    "/add/",
    status_code=200,
)
async def add_org_unit(
    add_org_unit: AddOrganizationUnit,
    current_user: dict = Depends(get_current_user),
):
    await manager.create_organization_unit(current_user, add_org_unit)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.delete(
    "/delete/",
    status_code=200,
)
async def delete_org(
    ou_dn: str,
    current_user: dict = Depends(get_current_user),
):
    await manager.delete_organization(current_user, ou_dn)
    return DEFAULT_SUCCESS_RESPONSE


@api_router.get("/list/", response_model=List[OrgDetail])
async def list_orgs(
    current_user: dict = Depends(get_current_user),
):
    res = await manager.list_ou(current_user)
    return res


@api_router.get("/get/", response_model=OrgDetail)
async def get_org(
    name: str,
    current_user: dict = Depends(get_current_user),
):
    res = await manager.get_org(current_user, name)
    return res
