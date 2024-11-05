from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class User(SQLModel, table=True):
    UserID: Optional[str] = Field(default=None, primary_key=True)
    WorkDirect: str
    WorkEmail: str
    FirstName: str
    MiddleNames: str
    LastName: str
    WorkPhone: str
    JobDescription: str
    IsActive: bool
    IsSupervisor: bool
    LogonName: str
