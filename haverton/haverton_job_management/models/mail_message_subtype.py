from odoo import fields, models


class MailMessageSubtype(models.Model):
    """ Class holding subtype definition for messages. Subtypes allow to tune
        the follower subscription, allowing only some subtypes to be pushed
        on the Wall. """
    _inherit = 'mail.message.subtype'
    _description = 'Message subtypes'

    haverton_code = fields.Selection(selection_add=[
        ('booking', 'Booking'),
    ])
