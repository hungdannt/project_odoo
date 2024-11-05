from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    is_printed = fields.Boolean() 
