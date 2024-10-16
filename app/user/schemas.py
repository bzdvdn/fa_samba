from typing import Optional
from time import time

from pydantic import BaseModel, validator

from app.config import settings


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires: int = settings.ACCESS_TOKEN_EXPIRE_SECONDS
    expires_in: int = 0

    @validator("expires_in")
    def generate_expirest_in(cls, v):
        return int(time() + settings.ACCESS_TOKEN_EXPIRE_SECONDS)


class AuthUser(BaseModel):
    username: str
    password: str


class UpdateUserPassword(AuthUser):
    pass


class AddUser(BaseModel):
    username: str
    password: str
    givenName: Optional[str] = None
    sn: Optional[str] = None
    mail: Optional[str] = None
    telephoneNumber: Optional[str] = None
    userAccountControl: Optional[int] = None
    pwdLastSet: Optional[int] = None
    accountExpires: Optional[int] = None
    userou: Optional[str] = None

    def to_user_request(self) -> dict:
        user_request = {
            "username": self.username,
            "password": self.password,
            "givenname": self.givenName,
            "surname": self.sn,
            "mailaddress": self.mail,
            "telephonenumber": self.telephoneNumber,
            "userou": self.userou,
        }
        return user_request


class UserList(BaseModel):
    users: list


class AddOrganizationUnit(BaseModel):
    ou_dn: str
    description: Optional[str] = None
    name: Optional[str] = None
    # sd: Optional[str] = None

    def to_request(self) -> dict:
        user_request = {
            "ou_dn": self.ou_dn,
            "description": self.description,
            "name": self.name,
            # "sd": self.sd,
        }
        return user_request


class MoveUserOU(BaseModel):
    from_ou: str
    to_ou: str
