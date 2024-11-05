from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobLocation(SQLModel, table=True):
    JobID: Optional[str] = Field(default=None, primary_key=True)
    LocationID: Optional[str] = Field(default=None, primary_key=True)
