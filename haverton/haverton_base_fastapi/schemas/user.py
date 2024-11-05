from odoo.http import request
from pydantic import Field

from .common import BaseModel, EmailConstraints

# Shared properties


class UserBase(BaseModel):
    uuid: str
    name: str = None
    avatar_256: str | bool = False
    login: str | bool = False
    email: str | bool = False
    phone: str | bool = False
    function: str | bool = None
    work_direct: str | bool = None
    is_supervisor: bool = None
    role: str | bool = None


# Properties to return via API
class User(UserBase):
    main_haverton_menu_key: str | bool = None
    total_unread_notifications: int | bool = None

    @property
    def fields_hidden(self):
        return self.get_fields_hidden_by_field_name('res.users', 'show_on_mobile_profile')

    @property
    def fields_required(self):
        return ['login', 'name', 'email', 'is_supervisor', 'role', 'uuid', 'avatar_256', 'main_haverton_menu_key', 'total_unread_notifications']


class UserMenuItem(BaseModel):
    name: str = None
    haverton_menu_key: str | bool = False
    is_main_menu_item: bool = False

    @classmethod
    def from_menu_item(cls, menu_item_in_db):
        return cls.model_construct(
            is_main_menu_item=menu_item_in_db['haverton_menu_key'] == request.env.user.main_haverton_menu_key,
            **menu_item_in_db
        )


# Properties to receive via API
class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserLogin(BaseModel):
    login: EmailConstraints = Field(
        title="The login name of the user account.")
    password: str


class UserLoginRefreshToken(BaseModel):
    refresh_token: str


class UserResetPassword(BaseModel):
    login: str = Field(
        default=None, title="The login name of the user account.")
    password: str = None
    confirm_password: str = None


class UserMentionSuggestion(BaseModel):
    uuid: str = None
    id: int = None
    name: str = None
