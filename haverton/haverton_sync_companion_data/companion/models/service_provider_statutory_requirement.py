from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class ServiceProviderStatutoryRequirement(SQLModel, table=True):
    ServiceProviderID: Optional[str] = Field(default=None, primary_key=True)
    StatutoryRequirementDomainNumber: Optional[str] = Field(
        default=None, primary_key=True)
    StatutoryRequirementCodeNumber: Optional[str] = Field(
        default=None, primary_key=True)
    CreationTime: datetime
    ExpiryDate: datetime
    ExpiryDateLastUpdatedTime: datetime
