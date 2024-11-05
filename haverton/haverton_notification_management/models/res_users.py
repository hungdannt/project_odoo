import json

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    notifications = fields.One2many('res.users.notification', 'user_id')
    total_unread_notifications = fields.Integer(
        compute='_compute_total_unread_notifications')

    def _auto_init(self):
        super()._auto_init()
        # add group_mobile_app_user for the existing users
        for rec in self.search([]):
            group_mobile_app_user = self.env.ref(
                'firebase_push_notification.group_mobile_app_user')
            if group_mobile_app_user and group_mobile_app_user.id not in rec.groups_id.ids:
                rec.groups_id = [(4, group_mobile_app_user.id)]

    @property
    def default_groups(self):
        res = super().default_groups
        res.append('firebase_push_notification.group_mobile_app_user')
        return res

    @api.depends('notifications', 'notifications.unread')
    def _compute_total_unread_notifications(self):
        for rec in self:
            rec.total_unread_notifications = self.env['res.users.notification'].search_count(
                [('user_id', '=', rec.id), ('unread', '=', True)])

    def send_in_app_notification(self, **kwargs: dict):
        self.ensure_one()
        recipient_ids = kwargs.pop('recipient_ids', [])
        user_notifications = []
        for partner_id in recipient_ids:
            user = self.search(
                [('partner_id', '=', partner_id)], limit=1)
            if user:
                user_notifications.append({
                    **kwargs,
                    'sender_id': self.partner_id.id,
                    'user_id': user.id,
                })
        return self.env['res.users.notification'].create(user_notifications)

    def send_notification(
        self,
        title,
        body,
        notification_type_id=None,
        target_action: str = None,
        screen_type: str = None,
        recipient_ids: list[int] = None,
        target_record_uuid: str = None,
        in_app: bool = False,
    ):
        """
        Functions:
        - send the push notification
        - send the in-app notification
        - save log
        """
        self.ensure_one()
        fb_message = self.env['res.partner.firebase.message'].create({
            'title': title,
            'body': body,
        })
        inapp_notification = []
        if in_app:
            inapp_notification = self.send_in_app_notification(
                title=title,
                body=body,
                notification_type_id=notification_type_id,
                target_action=target_action,
                screen_type=screen_type,
                recipient_ids=recipient_ids,
                target_record_uuid=target_record_uuid,
            )

            data = {
                "uuid": inapp_notification.uuid or "",
                "title": inapp_notification.title or "",
                "body": inapp_notification.body or "",
                "target_action": inapp_notification.target_action or "",
                "screen_type": inapp_notification.screen_type or "",
                "unread": "true" if inapp_notification.unread else "false",
                "target_record_uuid": inapp_notification.target_record_uuid or "",
                "create_date": inapp_notification.create_date.strftime("%Y-%m-%dT%H:%M:%SZ") if inapp_notification.create_date else "",
                "notification_type_id": json.dumps({
                    "code": inapp_notification.notification_type_id.code if inapp_notification.notification_type_id else "",
                    "name": inapp_notification.notification_type_id.name if inapp_notification.notification_type_id else "",
                })
            }
        try:
            fb_message.with_context(
                {'active_ids': recipient_ids}).channel_firebase_notifications_with_data(data)
            inapp_notification.push_notification_state = 'success'
        except Exception as e:
            inapp_notification.write({
                'push_notification_state': 'failed',
                'push_failed_reason': str(e)
            })
        return inapp_notification
