import json
from dateutil.parser import parse
from datetime import datetime, timedelta
from pytz import UTC

from fastapi import HTTPException
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
    MoveUserOU,
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

    async def get_users(self, current_user: dict):
        client = SambaClient(**current_user)
        return {"users": client.list_users()}

    async def create_user(
        self,
        current_user: dict,
        add_user: AddUser,
    ) -> dict:
        client = SambaClient(**current_user)
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

    async def delete_user(self, current_user: dict, username: str):
        client = SambaClient(**current_user)
        try:
            client.delete_user(username)
        except Exception as e:
            raise HTTPException(400, str(e))

    async def update_user_password(
        self,
        current_user: dict,
        update_user_password: UpdateUserPassword,
    ):
        client = SambaClient(**current_user)
        try:
            client.update_user_password(
                update_user_password.username,
                new_password=update_user_password.password,
            )
        except Exception as e:
            raise HTTPException(400, str(e))

    async def move_user_ou(
        self,
        current_user: dict,
        move: MoveUserOU,
    ):
        client = SambaClient(**current_user)
        try:
            client.move_user_ou(move.from_ou, move.to_ou)
        except Exception as e:
            raise HTTPException(400, str(e))


manager = AuthServiceManager()
