from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class WorkCategory(SQLModel, table=True):
    WorkCategoryID: Optional[str] = Field(default=None, primary_key=True)
    Description: str
