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


class UserGroupManage(BaseModel):
    groupname: str
    members: List[str]
