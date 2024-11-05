
from .common import BaseModel


class FilterItem(BaseModel):
    code: str | bool = None
    name: str | bool = None
