from odoo import fields, models
from firebase_admin import messaging


class ResPartnerFirebaseMessage(models.TransientModel):
    _inherit = "res.partner.firebase.message"

    def channel_firebase_notifications_with_data(self, data: dict):
        res_partner_ids = self._context.get('active_ids')
        device_ids = self.env['res.users'].sudo().search([('partner_id', 'in', res_partner_ids),
                                                          ]).mapped('mail_firebase_tokens').mapped('token')

        # See documentation on defining a message payload.
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=self.title or '',
                body=self.body or ''
            ),
            data=data,
            tokens=device_ids
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send_each_for_multicast(message)

        if response:
            notification_id = self.env['mobile.app.push.notification'].sudo().create({
                'name': self.title,
                'body': self.body,
                'send_notification_to': 'to_specefic',
                'partner_ids': [(6, 0, res_partner_ids)],
                'state': 'done',
            })

            self.env['push.notification.log.history'].sudo().create({
                'notification_id': notification_id.id,
                'date_send': fields.Datetime.now(),
                'notification_state': 'success',
            })
            responses = response.responses
            failed_tokens = []
            success_tokens = []
            for idx, resp in enumerate(responses):
                if not resp.success:
                    failed_tokens.append(device_ids[idx])
                if resp.success:
                    success_tokens.append(device_ids[idx])

            for succ in success_tokens:
                self.env['push.notification.log.partner'].sudo().create({
                    'notification_id': notification_id.id,
                    'name': self.title,  # this is the title of your notification
                    'body': self.body,
                    'partner_id': res_partner_ids[0],
                    'date_send': fields.Datetime.now(),
                    'notification_state': 'success',
                    'device_token': succ
                })
            for succ in failed_tokens:
                self.env['push.notification.log.partner'].sudo().create({
                    'notification_id': notification_id.id,
                    'name': self.title,  # this is the title of your notification
                    'body': self.body,
                    'partner_id': res_partner_ids[0],
                    'date_send': fields.Datetime.now(),
                    'notification_state': 'failed',
                    'device_token': succ
                })
