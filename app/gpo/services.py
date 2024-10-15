from fastapi.security import HTTPAuthorizationCredentials

from app.core.samba import SambaClient

from app.user.services import manager as auth_manager


class GPOService(object):
    async def list_gpo(self, credentials: HTTPAuthorizationCredentials):
        user_data = await auth_manager._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        return client.list_gpo()


manager = GPOService()
