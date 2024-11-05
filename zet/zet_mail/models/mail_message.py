from odoo import models, api


class Message(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self, values):
        res = super().create(values)
        if self._context.get('update_email_from_fetch_mail') and res.author_id:
            res.email_from = res.author_id.email_formatted if res.author_id.email_formatted else res.email_from
        return res  
