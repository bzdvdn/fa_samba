from typing import List

from pydantic import BaseModel


class Search(BaseModel):
    search_criteria: str
    search_target: List[str]
