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


class OrgDetail(BaseModel):
    dn: str
    ou: str
    name: str
    distinguishedName: str
    objectCategory: list
    objectClass: list
    whenCreated: str

    @classmethod
    def from_samba_message(cls, entry) -> "OrgDetail":
        return cls(
            dn=str(entry["dn"]),
            ou=str(entry["ou"]),
            name=str(entry["name"]),
            distinguishedName=str(entry["distinguishedName"]),
            whenCreated=str(entry["whenCreated"]),
            objectCategory=[o for o in entry.get("objectCategory", [])],
            objectClass=[o for o in entry.get("objectClass", [])],
        )
