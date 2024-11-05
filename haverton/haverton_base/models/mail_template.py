from odoo import  models, fields


class MailTemplate(models.Model):
    _inherit = "mail.template"

    allow_send_mail = fields.Boolean()

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
        return super(MailTemplate, self.with_context(allow_send_mail=self.allow_send_mail)).send_mail(res_id, force_send, raise_exception, email_values, notif_layout)
