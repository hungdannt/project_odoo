from .common import BaseModel


class Attachment(BaseModel):
    uuid: str | bool = None
    datas: str | bool = None
    local_url: str | bool = None


class AttachmentURL(BaseModel):
    uuid: str | bool = None
    local_url: str | bool = None
