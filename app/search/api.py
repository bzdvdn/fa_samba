from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.user.security import auth_scheme

from .schemas import Search
from .services import manager


api_router = APIRouter()


@api_router.post(
    "/",
)
async def search(
    search: Search, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    return await manager.search(credentials, search)
