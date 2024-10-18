from typing import List, Dict

from fastapi import APIRouter, Depends

from app.user.security import get_current_user

from .schemas import Search
from .services import manager


api_router = APIRouter()

SEARCH_RESPONSE = List[Dict]


@api_router.post("/", response_model=SEARCH_RESPONSE)
async def search(search: Search, current_user: dict = Depends(get_current_user)):
    return await manager.search(current_user, search)
