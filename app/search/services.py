from fastapi.security import HTTPAuthorizationCredentials

from app.core.samba import SambaClient

from app.user.services import manager as auth_manager

from .schemas import Search


class GPOService(object):
    async def search(self, credentials: HTTPAuthorizationCredentials, search: Search):
        user_data = await auth_manager._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        return client.search_criteria(
            search=search.search_criteria,
            search_target=search.search_target,
        )


manager = GPOService()
