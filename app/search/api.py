from typing import List, Dict

from fastapi import APIRouter, Depends

from app.user.security import get_current_user

from .schemas import Search, SearchDNRow, SearchByDN
from .services import manager


api_router = APIRouter()

SEARCH_RESPONSE = List[Dict]


@api_router.post("/", response_model=SEARCH_RESPONSE)
async def search(search: Search, current_user: dict = Depends(get_current_user)):
    return await manager.search(current_user, search)


@api_router.post(
    "/by_dn/",
    status_code=200,
    response_model=List[SearchDNRow],
)
async def search_by_dn(
    search_by_dn: SearchByDN,
    current_user: dict = Depends(get_current_user),
):
    res = await manager.search_by_dn(
        current_user,
        search_by_dn.dn,
        search_by_dn.object_classes,
        attrs=search_by_dn.attrs,
    )
    return res
