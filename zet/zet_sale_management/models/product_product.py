from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_note = fields.Many2one('product.note')
