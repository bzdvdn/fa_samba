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


class SambaClientError(Exception):
    pass


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
            if k in ("objectClass", "memberOf"):
                value = [i for i in entry[k]]
            else:
                value = entry.get(k, idx=0)
            if k == "dn":
                obj[k] = str(value)
            elif isinstance(value, bytes):
                obj[k] = value.decode(errors="ignore")
            elif value is None:
                obj[k] = value
            else:
                obj[k] = value
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
                attrs=[],
            )

            if len(lookup) == 0:
                return []
            users = []
            for entry in lookup:
                obj = self._parse_entry(entry)
                users.append(obj)
                # users.append("%s" % entry.get("samaccountname", idx=0))

        return users

    def _new_user(
        self,
        username: str,
        password: str,
        userou: Optional[str] = None,
        telephonenumber: Optional[str] = None,
        description: Optional[str] = None,
        givenname: Optional[str] = None,
        surname: Optional[str] = None,
        department: Optional[str] = None,
        mailaddress: Optional[str] = None,
        initials: Optional[str] = None,
        force_password_change_at_next_login_req: bool = False,
        setpassword: bool = False,
        **kwargs,
    ):
        displayname = self._client.fullname_from_names(
            given_name=givenname, initials=initials, surname=surname
        )
        cn = username
        if userou:
            user_dn = "CN=%s,%s,%s" % (cn, userou, self._client.domain_dn())
        else:
            user_dn = "CN=%s,%s" % (
                cn,
                self._client.get_wellknown_dn(
                    self._client.get_default_basedn(), dsdb.DS_GUID_USERS_CONTAINER
                ),
            )

        dnsdomain = (
            ldb.Dn(self._client, self._client.domain_dn())
            .canonical_str()
            .replace("/", "")
        )
        user_principal_name = "%s@%s" % (username, dnsdomain)
        # The new user record. Note the reliance on the SAMLDB module which
        # fills in the default information
        ldbmessage = {
            "dn": user_dn,
            "sAMAccountName": username,
            "userPrincipalName": user_principal_name,
            "objectClass": "user",
        }
        if surname is not None:
            ldbmessage["sn"] = surname

        if givenname is not None:
            ldbmessage["givenName"] = givenname

        if displayname != "":
            ldbmessage["displayName"] = displayname
            ldbmessage["name"] = displayname

        if initials is not None:
            ldbmessage["initials"] = "%s." % initials
        if description is not None:
            ldbmessage["description"] = description

        if mailaddress is not None:
            ldbmessage["mail"] = mailaddress
        if telephonenumber is not None:
            ldbmessage["telephoneNumber"] = telephonenumber
        if department is not None:
            ldbmessage["department"] = department

        for k, v in kwargs.items():
            ldbmessage[k] = str(v)

        with self.transaction():
            self._client.add(ldbmessage)
            if setpassword:
                self._client.setpassword(
                    f"(distinguishedName={ldb.binary_encode(user_dn)})",
                    password,
                    force_password_change_at_next_login_req,
                )

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
            raise SambaClientError(f"user with this `{username}` exists")
        with self.transaction():
            self._new_user(**user_data)
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

    def modify_user(
        self,
        username: str,
        sn: Optional[str] = None,
        telephoneNumber: Optional[str] = None,
        cn: Optional[str] = None,
        displayName: Optional[str] = None,
        givenName: Optional[str] = None,
        mail: Optional[str] = None,
        userAccountControl: Optional[str] = None,
    ) -> dict:
        user_obj = self.get_user_by_username(username)
        if not user_obj:
            raise SambaClientError(f"user with this `{username}` exists")
        ldbmessage = ldb.Message()
        ldbmessage.dn = ldb.Dn(self._client, str(user_obj["dn"]))
        if sn is not None:
            ldbmessage["sn"] = ldb.MessageElement(str(sn), ldb.FLAG_MOD_REPLACE, "sn")
        if telephoneNumber is not None:
            ldbmessage["telephoneNumber"] = ldb.MessageElement(
                str(telephoneNumber), ldb.FLAG_MOD_REPLACE, "telephoneNumber"
            )
        if cn is not None:
            ldbmessage["cn"] = ldb.MessageElement(str(cn), ldb.FLAG_MOD_REPLACE, "cn")
        if displayName is not None:
            ldbmessage["displayName"] = ldb.MessageElement(
                str(displayName), ldb.FLAG_MOD_REPLACE, "displayName"
            )
        if givenName is not None:
            ldbmessage["givenName"] = ldb.MessageElement(
                str(givenName), ldb.FLAG_MOD_REPLACE, "givenName"
            )
        if mail is not None:
            ldbmessage["mail"] = ldb.MessageElement(
                str(mail), ldb.FLAG_MOD_REPLACE, "mail"
            )
        if userAccountControl is not None:
            ldbmessage["userAccountControl"] = ldb.MessageElement(
                str(userAccountControl), ldb.FLAG_MOD_REPLACE, "userAccountControl"
            )
        with self.transaction():
            self._client.modify(ldbmessage)
        user_obj = self.get_user_by_username(username)
        if not user_obj:
            raise SambaClientError(
                f"user with this `{username}` exists after update..."
            )
        return user_obj
