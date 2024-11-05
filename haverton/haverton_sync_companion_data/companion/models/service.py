import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class Service(SQLModel, table=True):
    ServiceID: Optional[str] = Field(
        default=str(uuid.uuid4()).upper(), primary_key=True)
    Description: str
    ServiceTypeID: str
