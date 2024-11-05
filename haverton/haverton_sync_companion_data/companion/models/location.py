from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class Location(SQLModel, table=True):
    LocationID: Optional[str] = Field(default=None, primary_key=True)
    Name: str
    Sequence: int
    IsActive: bool
