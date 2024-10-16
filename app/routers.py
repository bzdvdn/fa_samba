from fastapi import APIRouter

from .user.api import api_router as user_router
from .gpo.api import api_router as gpo_router
from .search.api import api_router as search_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(gpo_router, prefix="/gpo", tags=["gpo"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
