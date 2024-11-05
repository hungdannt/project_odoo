from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class ServiceProviderRegion(SQLModel, table=True):
    ServiceProviderID: Optional[str] = Field(default=None, primary_key=True)
    RegionID: Optional[str] = Field(default=None, primary_key=True)
