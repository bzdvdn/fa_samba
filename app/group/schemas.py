from typing import Optional, List

from pydantic import BaseModel


class AddGroup(BaseModel):
    name: str
    groupou: Optional[str] = None
    grouptype: Optional[int] = None
    description: Optional[str] = None
    mailaddress: Optional[str] = None
    notes: Optional[str] = None
    # sd: Optional[str] = None

    def to_request(self) -> dict:
        return {
            "groupname": self.name,
            "groupou": self.groupou,
            "grouptype": self.grouptype,
            "description": self.description,
            "mailaddress": self.mailaddress,
            "notes": self.notes,
        }


class GroupUsersManage(BaseModel):
    groupname: str
    members: List[str]


class GroupMemeber(BaseModel):
    usermame: str
    telephoneNumber: Optional[str]
    mail: Optional[str]
    ou_dn: Optional[str]
