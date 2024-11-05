from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class PersonClientRelationship(SQLModel, table=True):
    PersonID: Optional[str] = Field(default=None, primary_key=True)
    ClientID: Optional[str] = Field(default=None, primary_key=True)
    IsPrimaryContact: bool
    IsSecondaryContact: bool
