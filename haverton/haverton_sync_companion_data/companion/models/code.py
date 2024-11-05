from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class Code(SQLModel, table=True):
    DomainNumber: Optional[int] = Field(default=None, primary_key=True)
    CodeNumber: Optional[int] = Field(default=None, primary_key=True)
    Name: str
