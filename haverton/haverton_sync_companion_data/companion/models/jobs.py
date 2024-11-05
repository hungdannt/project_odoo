from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class Jobs(SQLModel, table=True):
    JobId: Optional[str] = Field(default=None, primary_key=True)
    ContractNo: str
    ClientID: str
    AddressID: str
    StartDate: datetime
    EndDate: datetime
    WorkflowStatusLastUpdatedOnUTC: datetime
    RegionID: str
    ContractValueExGST: float
    ContractValueIncGST: float
    LastUpdatedOnUTC: datetime
    LastUpdatedBy: str
    WorkflowStatusID: str
    DocumentDirectoryNumber: int
    ContractStartDateDenormalised: datetime
    ContractEndDateDenormalised: datetime
