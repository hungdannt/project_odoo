from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class ServiceProviderServiceType(SQLModel, table=True):
    ServiceProviderID: Optional[str] = Field(default=None, primary_key=True)
    ServiceTypeID: Optional[str] = Field(default=None, primary_key=True)
