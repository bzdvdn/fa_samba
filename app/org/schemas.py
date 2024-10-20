from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


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


class SearchByOU(BaseModel):
    ou: str
    object_classes: List[str] = Field(min_items=1)
    attrs: Optional[list] = None


class SearchOURow(BaseModel):
    dn: str
    name: str
    objectClass: List[str]
    objectType: str
    description: Optional[str] = None
    extra_attrs: Optional[Dict[str, Any]] = None
