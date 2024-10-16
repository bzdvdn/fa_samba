from fastapi import APIRouter

from .user.api import api_router as user_router
from .gpo.api import api_router as gpo_router
from .search.api import api_router as search_router
from .group.api import api_router as group_router
from .org.api import api_router as org_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(gpo_router, prefix="/gpo", tags=["gpo"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(group_router, prefix="/group", tags=["group"])
api_router.include_router(org_router, prefix="/org", tags=["orgranization"])
