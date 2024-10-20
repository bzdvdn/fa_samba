from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class Search(BaseModel):
    search_criteria: str
    search_target: List[str]


class SearchByOU(BaseModel):
    ou: str
    object_classes: List[str] = Field(min_items=1)
    attrs: Optional[list] = None


class SearchDNRow(BaseModel):
    dn: str
    name: str
    objectClass: List[str]
    objectType: str
    description: Optional[str] = None
    extra_attrs: Optional[Dict[str, Any]] = None
