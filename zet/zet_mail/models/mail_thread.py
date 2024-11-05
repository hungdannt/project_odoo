from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_compute_subject(self):
        """ Get the default subject for a message posted in this record's
        discussion thread.

        :return str: default subject """
        self.ensure_one()
        return self._context.get('subject') or super()._message_compute_subject()

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        recipients_data = super()._notify_get_recipients(message, msg_vals, **kwargs)
        partner = self._context.get('partner')
        if partner:
            return [recipient for recipient in recipients_data if recipient['id'] == partner]
        return recipients_data
