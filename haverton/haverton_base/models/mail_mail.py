from odoo import _, api, fields, models


class MailMail(models.Model):
    _inherit = 'mail.mail'

    allow_send_mail = fields.Boolean()

    def send(self, auto_commit=False, raise_exception=False):
        for rec in self:
            if not rec.allow_send_mail:
                rec.state = 'exception'
                rec.failure_reason = 'To resume sending emails, please enable the allow send mail feature. Thank you!'
                continue
            super(MailMail, rec).send(auto_commit, raise_exception)

    @api.model
    def create(self, values):
        values['allow_send_mail'] = self._context.get(
            'allow_send_mail') or values.get('allow_send_mail')
        return super().create(values)
