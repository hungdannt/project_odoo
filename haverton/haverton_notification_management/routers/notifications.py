from typing import Annotated

from fastapi import APIRouter, Depends
from odoo import _
from odoo.addons.base.models.res_users import Users
from odoo.addons.haverton_base_fastapi.dependencies import authorize_session
from odoo.http import request

from ..schemas import UserNotification, UserNotificationUpdate
from ..utils import notification as noti_utils

router = APIRouter()


@router.put("/{uuid}", response_model=UserNotification)
def update_notification(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str,
    payload: UserNotificationUpdate,
):
    """
    Update notification
    """
    noti = request.env['res.users.notification'].validate_by_uuid(uuid)
    noti_utils.validate_notification(current_user, noti)
    noti.write(payload.dict())
    return noti


@router.delete("/{uuid}")
def delete_notification(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str,
):
    """
    Delete notification
    """
    noti = request.env['res.users.notification'].validate_by_uuid(uuid)
    noti_utils.validate_notification(current_user, noti)
    noti.active = False
    return {'detail': _('Notification was deleted successfully.')}
