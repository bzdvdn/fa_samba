from fastapi import APIRouter, Depends

from app.user.security import get_current_user

from .schemas import Search
from .services import manager


api_router = APIRouter()


@api_router.post(
    "/",
)
async def search(search: Search, current_user: dict = Depends(get_current_user)):
    return await manager.search(current_user, search)
