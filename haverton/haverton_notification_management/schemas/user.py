from datetime import datetime

from odoo.addons.haverton_base_fastapi.schemas import BaseModel
from pydantic import Field


class UserFcmToken(BaseModel):
    os: str | bool = Field(default=None, description="Device OS")
    token: str | bool = Field(default=None, description="Fcm Token")


class NotificationType(BaseModel):
    code: str | bool = None
    name: str | bool = None


class UserNotification(BaseModel):
    uuid: str = Field(default=None, description="UUID")
    title: str = Field(default=None, description="Title")
    body: str = Field(default=None, description="Body")
    target_action: str | bool = Field(
        default=None, description="Action when click on the notification")
    screen_type: str | bool = Field(
        default=None, description="Type of screen to do the target action")
    unread: bool = Field(default=None, description="Is unread notification?")
    target_record_uuid: str | bool = Field(
        default=None, description="Target record UUID")
    create_date: datetime = Field(default=None, description="Created On")
    notification_type_id: NotificationType | bool = Field(
        default=None, description="Notification Type")


class UserNotificationUpdate(BaseModel):
    unread: bool = Field(default=None, description="Is unread notification")


class UserLogout(BaseModel):
    fcm_token: str = None
