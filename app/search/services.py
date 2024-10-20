from typing import Optional, List

from app.core.samba import SambaClient

from .schemas import Search, SearchDNRow


class GPOService(object):
    async def search(self, current_user: dict, search: Search) -> list:
        client = SambaClient(**current_user)
        return client.search_criteria(
            search=search.search_criteria,
            search_target=search.search_target,
        )

    async def search_by_dn(
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
                    attr for attr in attrs if attr not in SearchDNRow.__fields__
                ]
            else:
                extra_attrs_list = []
            for entry in samba_entries:
                obj_class = [i for i in entry["objectClass"]]
                s_row = SearchDNRow(
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


manager = GPOService()
