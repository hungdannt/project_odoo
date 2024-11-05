from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class ServiceType(SQLModel, table=True):
    ServiceTypeID: Optional[str] = Field(default=None, primary_key=True)
    Description: str
    SystemCode: str
    WorkCategoryID: str
