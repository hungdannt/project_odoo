from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    stamp = fields.Binary(string="Stamp")
