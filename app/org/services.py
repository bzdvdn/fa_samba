from fastapi import HTTPException

from app.core.samba import SambaClient

from .schemas import AddOrganizationUnit


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


manager = OrgService()
