from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobActivityPredecessor(SQLModel, table=True):
    ActivityID: Optional[str] = Field(default=None, primary_key=True)
    PredecessorID: Optional[str] = Field(default=None, primary_key=True)
    JobID: str
