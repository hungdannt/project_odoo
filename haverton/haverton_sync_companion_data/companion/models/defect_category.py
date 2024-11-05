from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class DefectCategory(SQLModel, table=True):
    DefectCategoryID: Optional[str] = Field(default=None, primary_key=True)
    Name: str
    Type: int
    IsActive: bool
    IsDefaultNew: bool
    IsDefaultFromActivity: bool
