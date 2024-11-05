from typing import Annotated

from fastapi import APIRouter, Depends
from odoo import _
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import authorize_session
from odoo.http import request

from ..schemas import (
    NotificationType,
    UserFcmToken,
    UserNotification,
    UserNotificationUpdate,
)
from ..utils import notification as noti_utils

router = APIRouter()


@router.post("/me/fcm_token", response_model=UserFcmToken)
def save_my_fcm_token(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    fcm_token: UserFcmToken
):
    """
    Saves the new fcm_token for the current user
    """
    exists_token = request.env['mail.firebase'].sudo().search([('token', '!=', False), ('token', '=', fcm_token.token)])
    if exists_token:
        exists_token.sudo().unlink()
    mail_firebase = request.env['mail.firebase'].create({
        'user_id': current_user.id,
        'partner_id': current_user.partner_id.id,
        'os': fcm_token.os,
        'token': fcm_token.token,
    })
    return mail_firebase


@router.get("/me/notifications", response_model=PagedCollection[UserNotification])
def get_my_notifications(
    paging: Annotated[Paging, Depends(paging)],
    current_user: Annotated[Users | None, Depends(authorize_session)],
    unread: bool = None,
):
    """
    Get notifications of the current user
    """
    specification = dict(UserNotification())
    specification['notification_type_id'] = {
        'fields': dict(NotificationType())}
    domain = noti_utils.get_my_notifications_domain(current_user, filter_kwargs={
        'unread': unread,
    })
    res = request.env['res.users.notification'].web_search_read(
        domain=domain,
        specification=specification,
        order='create_date desc',
        limit=paging.limit,
        offset=paging.offset,
    )
    count = request.env['res.users.notification'].search_count(domain=domain)
    return PagedCollection[UserNotification](
        count=count,
        items=res['records']
    )


@router.put("/me/notifications")
def update_my_notifications(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    payload: UserNotificationUpdate,
):
    """
    Update all notifications of the current user
    """
    current_user.notifications.write(payload.model_dump())
    return {'detail': _('All notifications was updated successfully.')}


@router.get("/me/total_unread_notifications")
def count_unread_notifications(
    current_user: Annotated[Users | None, Depends(authorize_session)],
):
    """
    Count the total of unread notifications of the current user
    """
    domain = noti_utils.get_my_notifications_domain(current_user, filter_kwargs={
        'unread': True,
    })
    count = request.env['res.users.notification'].search_count(domain=domain)
    return count
