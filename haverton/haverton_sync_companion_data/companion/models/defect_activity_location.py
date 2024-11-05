from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class DefectActivityLocation(SQLModel, table=True):
    LocationID: Optional[str] = Field(default=None, primary_key=True)
    ActivityID: Optional[str] = Field(default=None, primary_key=True)
