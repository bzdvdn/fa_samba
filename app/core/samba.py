from typing import Optional

import ldb
from samba import dsdb
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

    def list_users(self) -> list:
        try:
            self._client.transaction_start()
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

            filter = "(&(objectClass=user)(userAccountControl:%s:=%u)%s%s)" % (
                ldb.OID_COMPARATOR_AND,
                dsdb.UF_NORMAL_ACCOUNT,
                filter_disabled,
                filter_expires,
            )

            lookup = self._client.search(
                search_dn,
                scope=ldb.SCOPE_SUBTREE,
                expression=filter,
                attrs=["samaccountname", "telephonenumber", "mail", "dn"],
            )

            if len(lookup) == 0:
                return []
            users = []
            for entry in lookup:
                dn_obj = entry.get("dn", idx=0)
                obj = {
                    "usermame": entry.get("samaccountname", idx=0),
                    "telephonenumber": entry.get("telephonenumber", idx=0),
                    "mail": entry.get("mail", idx=0),
                    "ou_dn": str(dn_obj) if dn_obj else None,
                }
                users.append(obj)
                # users.append("%s" % entry.get("samaccountname", idx=0))
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()

        return users

    def create_user(
        self,
        user_data: dict,
        userAccountControl: Optional[int],
        pwdLastSet: Optional[int],
        accountExpires: Optional[int],
    ) -> dict:
        try:
            self._client.transaction_start()
            self._client.newuser(**user_data)
            username = user_data["username"]
            search_filter = f"(sAMAccountName={username})"
            if accountExpires is not None:
                self._client.setexpiry(search_filter, int(accountExpires))
            if pwdLastSet is not None:
                self._client.force_password_change_at_next_login(search_filter)
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()
        return {}

    def delete_user(self, username: str):
        try:
            self._client.transaction_start()
            self._client.deleteuser(username=username)
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()

    def update_user_password(self, username: str, new_password: str):
        try:
            self._client.transaction_start()
            search_filter = f"(sAMAccountName={username})"
            self._client.setpassword(
                search_filter,
                new_password,
                force_change_at_next_login=False,
                username=None,
            )
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()

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
        try:
            self._client.transaction_start()
            self._client.create_ou(
                ou_dn=ou_dn,
                description=description,
                name=name,
                sd=sd,
            )
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()

    def delete_organization_unit(self, ou_dn: str):
        try:
            self._client.transaction_start()
            self._client.delete(ou_dn)
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()

    def move_user_ou(self, from_ou: str, to_ou: str):
        try:
            self._client.transaction_start()
            self._client.rename(from_ou, to_ou)
        except:
            self._client.transaction_cancel()
            raise
        else:
            self._client.transaction_commit()
