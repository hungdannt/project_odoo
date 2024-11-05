from odoo import models, fields


class IrModel(models.Model):
    _inherit = 'ir.model'

    custome_icon = fields.Binary()
    