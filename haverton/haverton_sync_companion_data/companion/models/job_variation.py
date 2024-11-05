from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class JobVariation(SQLModel, table=True):
    VariationId: Optional[str] = Field(default=None, primary_key=True)
    JobId: str
    VariationNumber: int
    StartDate: datetime
    CreatedOnUTC: datetime
    Summary: str

    Reference: str
    InvoiceNumber: str
    # reason
    VariationReasonDomain: int
    VariationReasonCode: int
    # approval
    VariationApprovalDomain: int
    VariationApprovalCode: int
    CreatedBy: str
    VariationApprovalLastUpdatedBy: str

    @property
    def haverton_task_type(self) -> str:
        return 'variation'
