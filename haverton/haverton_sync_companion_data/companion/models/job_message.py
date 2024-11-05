from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobMessage(SQLModel, table=True):
    JobID: Optional[str] = Field(default=None, primary_key=True)
    MessageID: Optional[str] = Field(default=None, primary_key=True)
