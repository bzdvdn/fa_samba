from fastapi import HTTPException

from app.core.samba import SambaClient

from .schemas import AddOrganizationUnit, OrgDetail


class OrgService(object):
    async def delete_organization(
        self,
        current_user: dict,
        ou_dn: str,
    ):
        client = SambaClient(**current_user)
        try:
            client.delete_organization_unit(ou_dn)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def create_organization_unit(
        self,
        current_user: dict,
        add_org_unit: AddOrganizationUnit,
    ):
        client = SambaClient(**current_user)
        try:
            client.create_organization_unit(**add_org_unit.to_request())
        except Exception as e:
            raise HTTPException(400, str(e))

    async def list_ou(self, current_user: dict) -> list:
        client = SambaClient(**current_user)
        try:
            res = client.list_ou()
            return [OrgDetail.from_samba_message(e) for e in res]
        except Exception as e:
            raise HTTPException(400, str(e))

    async def get_org(self, current_user: dict, name: str) -> OrgDetail:
        client = SambaClient(**current_user)
        try:
            entry = client.get_ou(name)
        except Exception as e:
            raise HTTPException(400, str(e))
        if not entry:
            raise HTTPException(404, f"ou with name - `{name}` does not exists.")
        return OrgDetail.from_samba_message(entry)


manager = OrgService()
