from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .common import SQLModel


class Message(SQLModel, table=True):
    MessageID: Optional[str] = Field(default=None, primary_key=True)
    FromUserID: str
    ServiceProviderID: str
    Subject: str
    MessageText: str
    MessageType: int
    CreatedOnUTC: datetime

    MessageType: int = Field(default=1)
    NotifyEveryone: bool = Field(default=False)
    PersistentAlert: bool = Field(default=False)
    SmsSent: bool = Field(default=False)
