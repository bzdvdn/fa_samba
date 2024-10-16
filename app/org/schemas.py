from typing import Optional

from pydantic import BaseModel


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
