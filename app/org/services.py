from typing import List, Optional

from fastapi import HTTPException

from app.core.samba import SambaClient

from .schemas import AddOrganizationUnit, SearchOURow


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

    async def search_by_ou(
        self,
        current_user: dict,
        ou: str,
        object_classes: List[str],
        attrs: Optional[list] = None,
    ) -> list:
        client = SambaClient(**current_user)
        try:
            samba_entries = client.search_by_ou(
                ou=ou, object_classes=object_classes, attrs=attrs
            )
            res = []
            if attrs:
                extra_attrs_list = [
                    attr for attr in attrs if attr not in SearchOURow.__fields__
                ]
            else:
                extra_attrs_list = []
            for entry in samba_entries:
                obj_class = [i for i in entry["objectClass"]]
                s_row = SearchOURow(
                    dn=str(entry.get("dn")),
                    name=entry.get("name", idx=0),
                    objectClass=obj_class,
                    objectType=obj_class[-1],
                    description=entry.get("description", idx=0),
                )
                s_row.extra_attrs = {
                    f: str(entry.get(f, idx=0)) for f in extra_attrs_list
                }
                res.append(s_row)
            return res
        except Exception as e:
            raise


manager = OrgService()
