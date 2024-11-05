from datetime import datetime
from enum import Enum
from typing import List

from .attachment import Attachment
from .common import BaseModel


class MessageSubtypeCode(str, Enum):
    note = 'note'


class MessageAuthor(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    avatar_256: str | bool = False


class MessageSubtype(BaseModel):
    haverton_code: str | bool = None
    name: str | bool = None


class MessageBase(BaseModel):
    uuid: str | bool = None
    author_id: MessageAuthor | bool = None
    date: datetime | bool = None
    subject: str | bool = None
    body: str | bool = None
    task_booked_start_date: datetime | bool = None
    subtype_id: MessageSubtype | bool = None
    attachment_ids: List[Attachment] | bool = None


class Message(MessageBase):
    pass


class MessageCreate(BaseModel):
    subject: str | bool = None
    body: str | bool = None
    user_uuids: list[str] | bool | None = None


class MessageCreateWithAttachment(MessageCreate):
    attachment_uuids: List[str] | bool = None
