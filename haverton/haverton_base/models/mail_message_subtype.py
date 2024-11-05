from odoo import fields, models


class MailMessageSubtype(models.Model):
    """ Class holding subtype definition for messages. Subtypes allow to tune
        the follower subscription, allowing only some subtypes to be pushed
        on the Wall. """
    _inherit = 'mail.message.subtype'
    _description = 'Message subtypes'

    haverton_code = fields.Selection([
        ('note', 'Note'),
    ], help='Code to identify for the subtype used in the Haverton app.')

    _sql_constraints = [
        (
            "haverton_code_unique",
            "unique(haverton_code)",
            "The subtype with this haverton_code is existed.",
        )
    ]

    def browse_by_haverton_code(self, code: str):
        return self.search([('haverton_code', '=', code)], limit=1)
