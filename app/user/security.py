from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .services import manager

auth_scheme = HTTPBearer(bearerFormat="Bearer", description="Access Bearer Token")


async def get_current_credential(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> dict:
    return await manager.verify_access_token(credentials)
