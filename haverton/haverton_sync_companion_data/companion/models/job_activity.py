import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobActivity(SQLModel, table=True):
    ActivityID: Optional[str] = Field(
        default=str(uuid.uuid4()).upper(), primary_key=True)
    JobID: str
    Sequence: int
    BookedStartDate: datetime
    ForecastedStartDate: datetime
    StartDate: datetime
    CompletionDate: datetime
    ForecastedCompletionDate: datetime
    ServiceProviderID: str
    UserID: str
    LinkedJobActivity: str
    DefectCategoryID: str
    DefectType: str
    BookingConfirmedOn: datetime
    CreatedOnUTC: datetime
    CreatedBy: str
    VariationId: str
    DefectAction: str
    DefectDescription: str
    DefectDetail: str
    IsBackCharged: bool
    Duration: int
    BackChargedServiceProviderID: str
    BackChargedAmount: float

    # TODO update default value
    ServiceID: str = Field(default='5B277FF2-B9D6-478F-AD32-01FAFD66AC12')
    Offset: int = Field(default=0)
    Stoppage: int = Field(default=0)
    JobActivityType: int = Field(default=1)
    ReforecastBaseline: int = Field(default=0)
    Milestone: int = Field(default=0)
    BaselineOffset: int = Field(default=0)
    BaselineDuration: int = Field(default=1)
    NotApplicable: int = Field(default=0)
    MasterSubBulkChangeable: int = Field(default=0)
    IsContractTrigger: int = Field(default=0)
    IsContractComparison: int = Field(default=0)
    ShouldWorkChainPropagateBookedStartDate: int = Field(default=1)
    ShouldWorkChainPropagateCompletionNA: int = Field(default=1)
    AutoCarbonCopyUponCompletion: int = Field(default=0)

    @property
    def haverton_task_type(self) -> str:
        return 'defect' if self.DefectCategoryID else 'activity'
