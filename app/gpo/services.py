from app.core.samba import SambaClient


class GPOService(object):
    async def list_gpo(self, current_user: dict):
        client = SambaClient(**current_user)
        return client.list_gpo()


manager = GPOService()
