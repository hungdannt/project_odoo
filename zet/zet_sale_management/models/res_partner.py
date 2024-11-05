from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    price_list_ids = fields.Many2many('product.pricelist', string="Optional Price List")
