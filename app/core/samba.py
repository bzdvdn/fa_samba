from typing import Optional, List
from contextlib import contextmanager

import ldb
from samba import dsdb  # type: ignore
from samba.netcmd.gpo import get_gpo_info, attr_default, gpo_flags_string
from samba.auth import system_session
from samba.credentials import Credentials
from samba.param import LoadParm
from samba.samdb import SamDB

from fastapi import HTTPException

from app.config.settings import SAMBA_HOST


class SambaClient(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._client = self._init_client()

    def _init_client(self) -> SamDB:
        lp = LoadParm()
        creds = Credentials()
        creds.guess(lp)
        creds.set_username(self.username)
        creds.set_password(self.password)
        try:
            samdb = SamDB(
                url=SAMBA_HOST,
                session_info=system_session(),
                credentials=creds,
                lp=lp,
            )
            return samdb
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid username or password")

    @contextmanager
    def transaction(self):
        self._client.transaction_start()
        try:
            yield
        except:
            self._client.transaction_cancel()
            raise
        finally:
            self._client.transaction_commit()

    def _parse_entry(self, entry) -> dict:
        obj = {}
        for k in entry:
            value = entry.get(k, idx=0)
            if isinstance(value, bytes):
                obj[k] = value.decode(errors="ignore")
            elif value is None:
                obj[k] = value
            else:
                obj[k] = str(value)
        return obj

    def list_users(self) -> list:
        with self.transaction():
            search_dn = self._client.domain_dn()
            filter_expires = ""
            current_nttime = self._client.get_nttime()
            filter_expires = "(|(accountExpires=0)(accountExpires>=%u))" % (
                current_nttime
            )
            filter_disabled = "(!(userAccountControl:%s:=%u))" % (
                ldb.OID_COMPARATOR_AND,
                dsdb.UF_ACCOUNTDISABLE,
            )

            filter_ = "(&(objectClass=user)(userAccountControl:%s:=%u)%s%s)" % (
                ldb.OID_COMPARATOR_AND,
                dsdb.UF_NORMAL_ACCOUNT,
                filter_disabled,
                filter_expires,
            )

            lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=filter_,
                attrs=["*"],
            )

            if len(lookup) == 0:
                return []
            users = []
            for entry in lookup:
                obj = self._parse_entry(entry)
                users.append(obj)
                # users.append("%s" % entry.get("samaccountname", idx=0))

        return users

    def create_user(
        self,
        user_data: dict,
        userAccountControl: Optional[int],
        pwdLastSet: Optional[int],
        accountExpires: Optional[int],
    ) -> dict:
        username = user_data["username"]
        db_user = self.get_user_by_username(username=username)
        if db_user:
            raise ValueError(f"user with this `{username}` exists")
        with self.transaction():
            self._client.newuser(**user_data)
            username = user_data["username"]
            search_filter = f"(sAMAccountName={username})"
            if pwdLastSet is not None:
                self._client.force_password_change_at_next_login(search_filter)
        if accountExpires is not None:
            self._client.setexpiry(search_filter, int(accountExpires))

        return {}

    def delete_user(self, username: str):
        with self.transaction():
            self._client.transaction_start()
            self._client.deleteuser(username=username)

    def get_user_by_username(self, username: str) -> Optional[dict]:
        with self.transaction():
            search_dn = self._client.domain_dn()
            search_filter = f"(sAMAccountName={username})"
            lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=search_filter,
                attrs=["*"],
            )
            if len(lookup) == 0:
                return None
            obj = self._parse_entry(lookup[0])
            return obj

    def update_user_password(self, username: str, new_password: str):
        with self.transaction():
            search_filter = f"(sAMAccountName={username})"
            self._client.setpassword(
                search_filter,
                new_password,
                force_change_at_next_login=False,
                username=None,
            )

    def list_gpo(self) -> list:
        gpos = []
        msg = get_gpo_info(self._client, None)

        for m in msg:
            # print("DEBUG: " + str(m['name'][0]))
            gpo = {
                # str(m['name'][0]).split("'")[1::2]
                "gpo": str(m["name"][0]),
                "displayname": str(m["displayName"][0]),
                "path": str(m["gPCFileSysPath"][0]),
                "dn": str(m.dn),
                "version": str(attr_default(m, "versionNumber", "0")),
                "flags": gpo_flags_string(int(attr_default(m, "flags", 0))),
            }
            gpos.append(gpo)
        return gpos

    def create_organization_unit(
        self,
        ou_dn: str,
        description: Optional[str] = None,
        name: Optional[str] = None,
        sd: Optional[str] = None,
    ):
        with self.transaction():
            self._client.transaction_start()
            self._client.create_ou(
                ou_dn=ou_dn,
                description=description,
                name=name,
                sd=sd,
            )

    def delete_organization_unit(self, ou_dn: str):
        with self.transaction():
            self._client.transaction_start()
            self._client.delete(ou_dn)

    def move_user_ou(self, from_ou: str, to_ou: str):
        with self.transaction():
            self._client.transaction_start()
            self._client.rename(from_ou, to_ou)

    def add_group(self, group_request: dict):
        with self.transaction():
            self._client.transaction_start()
            self._client.newgroup(**group_request)

    def delete_group(self, groupname: str):
        with self.transaction():
            self._client.transaction_start()
            self._client.deletegroup(groupname)

    def _add_or_remove_users_to_group(
        self, groupname: str, members: List[str], to_add: bool = True
    ):
        with self.transaction():
            self._client.transaction_start()
            self._client.add_remove_group_members(
                groupname, members, add_members_operation=to_add
            )

    def add_users_to_group(self, groupname: str, members: List[str]):
        return self._add_or_remove_users_to_group(
            groupname=groupname, members=members, to_add=True
        )

    def remove_users_from_group(self, groupname: str, members: List[str]):
        return self._add_or_remove_users_to_group(
            groupname=groupname, members=members, to_add=False
        )

    def list_groups(
        self,
    ):
        result = []
        with self.transaction():
            search_dn = self._client.domain_dn()
            # filter_str = "(objectclass=group)"
            filter_str = "(objectclass=group)"
            lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=filter_str,
                attrs=[
                    "samaccountname",
                    "groupType",
                    "description",
                    "mail",
                    "info",
                ],
            )
            if len(lookup) == 0:
                return []

            for entry in lookup:
                obj = {
                    "sAMAccountName": entry.get("samaccountname", idx=0),
                    "groupType": entry.get("groupType", idx=0),
                    "description": entry.get("description", idx=0),
                    "mail": entry.get("mail", idx=0),
                    "info": entry.get("info", idx=0),
                }
                result.append(obj)
        return result

    def list_users_by_group(self, groupname: str):
        result = []
        with self.transaction():
            search_dn = self._client.domain_dn()
            group_str = f"(sAMAccountName={groupname})"
            group_lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=group_str,
                attrs=["distinguishedName", "member"],
            )
            if len(group_lookup) == 0:
                self._client.transaction_commit()
                return []
            dn = group_lookup[0].get("distinguishedName", idx=0)
            filter_query = f"(&(objectclass=user)(memberOf={dn}))"
            lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=filter_query,
                attrs=["samaccountname", "telephonenumber", "mail", "dn"],
            )

            if len(lookup) == 0:
                self._client.transaction_commit()
                return []
            for entry in lookup:
                dn_obj = entry.get("dn", idx=0)
                obj = {
                    "usermame": entry.get("samaccountname", idx=0),
                    "telephonenumber": entry.get("telephonenumber", idx=0),
                    "mail": entry.get("mail", idx=0),
                    "ou_dn": str(dn_obj) if dn_obj else None,
                }
                result.append(obj)
        return result

    def search_criteria(self, search: str, search_target: List[str]):
        search_dn = self._client.domain_dn()
        result = []
        with self.transaction():
            lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=search,
                attrs=search_target,
            )
            for entry in lookup:
                row = {k: str(entry.get(k, idx=0)) for k in search_target}
                result.append(row)
