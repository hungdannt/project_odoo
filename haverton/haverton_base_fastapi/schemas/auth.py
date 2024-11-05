from .common import BaseModel


# Properties to receive via API
class RefreshTokenCreate(BaseModel):
    password: str


class RefreshTokenDelete(BaseModel):
    refresh_token: str
    password: str
