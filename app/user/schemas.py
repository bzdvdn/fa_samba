from typing import Optional, List
from time import time

from pydantic import BaseModel, validator

from app.config import settings


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires: int = settings.ACCESS_TOKEN_EXPIRE_SECONDS
    expires_in: int = 0

    @validator("expires_in")
    def generate_expires_in(cls, v):
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


class UserRow(BaseModel):
    dn: Optional[str]
    objectClass: Optional[str]
    cn: Optional[str]
    sn: Optional[str]
    telephoneNumber: Optional[str]
    givenName: Optional[str]
    instanceType: Optional[str]
    whenCreated: Optional[str]
    whenChanged: Optional[str]
    displayName: Optional[str]
    uSNCreated: Optional[str]
    name: Optional[str]
    objectGUID: Optional[bytes]
    badPwdCount: Optional[str]
    codePage: Optional[str]
    countryCode: Optional[str]
    badPasswordTime: Optional[str]
    lastLogoff: Optional[str]
    lastLogon: Optional[str]
    primaryGroupID: Optional[str]
    objectSid: Optional[str]
    accountExpires: Optional[str]
    logonCount: Optional[str]
    sAMAccountName: Optional[str]
    sAMAccountType: Optional[str]
    userPrincipalName: Optional[str]
    objectCategory: Optional[str]
    mail: Optional[str]
    pwdLastSet: Optional[str]
    userAccountControl: Optional[str]
    uSNChanged: Optional[str]
    memberOf: Optional[str]
    distinguishedName: Optional[str]


class UserList(BaseModel):
    users: List[UserRow]


class MoveUserOU(BaseModel):
    from_ou: str
    to_ou: str


class UpdateTokensSchema(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    sn: Optional[str] = None
    telephoneNumber: Optional[str] = None
    cn: Optional[str] = None
    displayName: Optional[str] = None
    givenName: Optional[str] = None
    mail: Optional[str] = None

    def to_request(self) -> dict:
        user_request = {
            "sn": self.sn,
            "telephoneNumber": self.telephoneNumber,
            "cn": self.cn,
            "displayName": self.displayName,
            "givenName": self.givenName,
            "mail": self.mail,
        }
        return user_request
