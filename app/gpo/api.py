from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.user.security import auth_scheme
from .services import manager


api_router = APIRouter()


@api_router.get(
    "/",
)
async def list_gpo(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return await manager.list_gpo(credentials)
