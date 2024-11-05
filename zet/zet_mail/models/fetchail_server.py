from odoo import api,  models, SUPERUSER_ID


class FetchmailServer(models.Model):
    """Incoming POP/IMAP mail server account"""

    _inherit = 'fetchmail.server'

    @api.model
    def fetch_mails(self):
        return self.with_user(SUPERUSER_ID).with_context({'update_email_from_fetch_mail': True})._fetch_mails()

    @api.model
    def get_show_button_fetch_email(self):
        return self.sudo().search_count([('state', '=', 'done'), ('server_type', '!=', 'local')])
