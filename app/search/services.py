from app.core.samba import SambaClient

from .schemas import Search


class GPOService(object):
    async def search(self, current_user: dict, search: Search):
        client = SambaClient(**current_user)
        return client.search_criteria(
            search=search.search_criteria,
            search_target=search.search_target,
        )


manager = GPOService()
