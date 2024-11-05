from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class WorkflowStatus(SQLModel, table=True):
    WorkflowStatusID: Optional[str] = Field(default=None, primary_key=True)
    Name: str
    DefectStatus: bool
    SystemCode: str
    IsActive: bool
    IsActiveWorkflow: bool
    Sequence: int
    IsAutoRecalculatedStatus: bool
    IsOnHold: bool
    CreatedOnUTC: datetime
