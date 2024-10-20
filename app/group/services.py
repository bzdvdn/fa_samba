from typing import Optional

from fastapi import HTTPException

from app.core.samba import SambaClient

from .schemas import (
    AddGroup,
    GroupUsersManage,
    GroupDetail,
)


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
        user_group_manage: GroupUsersManage,
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
        user_group_manage: GroupUsersManage,
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
            return [GroupDetail.from_samba_message(row) for row in result]
        except Exception as e:
            raise HTTPException(400, str(e))

    async def list_users_by_group(self, current_user: dict, groupname: str) -> list:
        client = SambaClient(**current_user)
        try:
            result = client.list_users_by_group(groupname)
            return result
        except Exception as e:
            raise HTTPException(400, str(e))

    async def get_group_by_name(
        self, current_user: dict, groupname: str
    ) -> Optional[GroupDetail]:
        client = SambaClient(**current_user)
        try:
            group = client.get_group_by_name(name=groupname)
            if group:
                return GroupDetail.from_samba_message(group)
            return None
        except Exception as e:
            raise HTTPException(400, str(e))


manager = GroupService()
