from fastapi import APIRouter, Depends

from app.user.security import get_current_user
from .services import manager


api_router = APIRouter()


@api_router.get(
    "/",
)
async def list_gpo(current_user: dict = Depends(get_current_user)):
    return await manager.list_gpo(current_user)
