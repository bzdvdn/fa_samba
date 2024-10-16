from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .services import manager

auth_scheme = HTTPBearer(bearerFormat="Bearer", description="Access Bearer Token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> dict:
    return await manager._verify_token(credentials.credentials, "access")
