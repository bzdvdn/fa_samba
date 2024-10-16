import os
import json
from dateutil.parser import parse
from datetime import datetime, timedelta
from pytz import UTC

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config.settings import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    SECRET_KEY,
    SECRET_SALT,
)
from app.core.samba import SambaClient
from app.utils.crypt import Crypt

from .schemas import (
    TokenData,
    AddUser,
    UpdateUserPassword,
    AddOrganizationUnit,
    MoveUserOU,
    AddGroup,
    UserGroupManage,
)

crypt = Crypt(SECRET_SALT)


class AuthServiceManager:
    ALGORITHM = "HS256"

    async def auth(self, username: str, password: str) -> TokenData:
        client = SambaClient(username, password)
        sub = json.dumps({"username": username, "password": password})
        return TokenData(
            access_token=self.generate_access_token(sub),
        )

    def generate_access_token(self, sub: str) -> str:
        return self._craete_token(sub, ACCESS_TOKEN_EXPIRE_SECONDS)

    def _craete_token(self, sub: str, expire_delta: int) -> str:
        token_sub = crypt.encrypt(sub, SECRET_KEY)
        data = {
            "sub": token_sub,
            "expire": str(datetime.now(UTC) + timedelta(seconds=expire_delta)),
        }
        return jwt.encode(data, SECRET_KEY, algorithm=self.ALGORITHM)

    async def _verify_token(self, token: str) -> dict:
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[self.ALGORITHM])
            expire_time = parse(decoded["expire"])
            if datetime.now(UTC) >= expire_time:
                raise HTTPException(
                    status_code=401,
                    detail="token expires.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token_sub: str = decoded["sub"]
            user_data = json.loads(crypt.decrypt(token_sub, SECRET_KEY))
            return user_data
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="invalid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=403,
                detail="invalid token 2.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def verify_access_token(
        self, credentials: HTTPAuthorizationCredentials
    ) -> dict:
        user_data = await self._verify_token(credentials.credentials)
        return {"username": user_data["username"]}

    async def get_me(self, credentials: HTTPAuthorizationCredentials):
        me: dict = await self.verify_access_token(credentials)
        return me

    async def get_users(self, credentials: HTTPAuthorizationCredentials):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        return {"users": client.list_users()}

    async def create_user(
        self,
        credentials: HTTPAuthorizationCredentials,
        add_user: AddUser,
    ) -> dict:
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        user_data = add_user.to_user_request()
        try:
            result = client.create_user(
                user_data=user_data,
                userAccountControl=add_user.userAccountControl,
                pwdLastSet=add_user.pwdLastSet,
                accountExpires=add_user.accountExpires,
            )
            return result
        except Exception as e:
            raise HTTPException(400, str(e))

    async def delete_user(
        self, credentials: HTTPAuthorizationCredentials, username: str
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.delete_user(username)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def update_user_password(
        self,
        credentials: HTTPAuthorizationCredentials,
        update_user_password: UpdateUserPassword,
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.update_user_password(
                update_user_password.username,
                new_password=update_user_password.password,
            )
        except Exception as e:
            raise HTTPException(400, str(e))

    async def create_organization_unit(
        self,
        credentials: HTTPAuthorizationCredentials,
        add_org_unit: AddOrganizationUnit,
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.create_organization_unit(**add_org_unit.to_request())
        except Exception as e:
            raise HTTPException(400, str(e))

    async def move_user_ou(
        self,
        credentials: HTTPAuthorizationCredentials,
        move: MoveUserOU,
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.move_user_ou(move.from_ou, move.to_ou)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def delete_organization(
        self,
        credentials: HTTPAuthorizationCredentials,
        ou_dn: str,
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.delete_organization_unit(ou_dn)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def add_group(
        self, credentials: HTTPAuthorizationCredentials, add_group: AddGroup
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.add_group(add_group.to_request())
        except Exception as e:
            raise HTTPException(400, str(e))

    async def delete_group(
        self, credentials: HTTPAuthorizationCredentials, groupname: str
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.delete_group(groupname)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def add_users_to_group(
        self,
        credentials: HTTPAuthorizationCredentials,
        user_group_manage: UserGroupManage,
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.add_users_to_group(
                user_group_manage.groupname, user_group_manage.members
            )
        except Exception as e:
            raise HTTPException(400, str(e))

    async def remove_users_from_group(
        self,
        credentials: HTTPAuthorizationCredentials,
        user_group_manage: UserGroupManage,
    ):
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            client.remove_users_from_group(
                user_group_manage.groupname, user_group_manage.members
            )
        except Exception as e:
            raise HTTPException(400, str(e))

    async def list_groups(self, credentials: HTTPAuthorizationCredentials) -> list:
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            result = client.list_groups()
            return result
        except Exception as e:
            raise HTTPException(400, str(e))

    async def list_users_by_group(
        self, credentials: HTTPAuthorizationCredentials, groupname: str
    ) -> list:
        user_data = await self._verify_token(credentials.credentials)
        client = SambaClient(**user_data)
        try:
            result = client.list_users_by_group(groupname)
            return result
        except Exception as e:
            raise HTTPException(400, str(e))


manager = AuthServiceManager()
