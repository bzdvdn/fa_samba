from fastapi import HTTPException

from app.config.settings import (
    SECRET_SALT,
)
from app.core.samba import SambaClient
from app.utils.crypt import Crypt

from .schemas import (
    AddGroup,
    UserGroupManage,
)

crypt = Crypt(SECRET_SALT)


class GroupService(object):
    async def add_group(self, current_user: dict, add_group: AddGroup):
        client = SambaClient(**current_user)
        try:
            client.add_group(add_group.to_request())
        except Exception as e:
            raise HTTPException(400, str(e))

    async def delete_group(self, current_user: dict, groupname: str):
        client = SambaClient(**current_user)
        try:
            client.delete_group(groupname)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def add_users_to_group(
        self,
        current_user: dict,
        user_group_manage: UserGroupManage,
    ):
        client = SambaClient(**current_user)
        try:
            client.add_users_to_group(
                user_group_manage.groupname, user_group_manage.members
            )
        except Exception as e:
            raise HTTPException(400, str(e))

    async def remove_users_from_group(
        self,
        current_user: dict,
        user_group_manage: UserGroupManage,
    ):
        client = SambaClient(**current_user)
        try:
            client.remove_users_from_group(
                user_group_manage.groupname, user_group_manage.members
            )
        except Exception as e:
            raise HTTPException(400, str(e))

    async def list_groups(
        self,
        current_user: dict,
    ) -> list:
        client = SambaClient(**current_user)
        try:
            result = client.list_groups()
            return result
        except Exception as e:
            raise HTTPException(400, str(e))

    async def list_users_by_group(self, current_user: dict, groupname: str) -> list:
        client = SambaClient(**current_user)
        try:
            result = client.list_users_by_group(groupname)
            return result
        except Exception as e:
            raise HTTPException(400, str(e))


manager = GroupService()
