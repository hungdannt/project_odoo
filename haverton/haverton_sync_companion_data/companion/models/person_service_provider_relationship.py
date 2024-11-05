from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class PersonServiceProviderRelationship(SQLModel, table=True):
    PersonID: Optional[str] = Field(default=None, primary_key=True)
    ServiceProviderID: Optional[str] = Field(default=None, primary_key=True)
    IsPrimaryContact: bool
