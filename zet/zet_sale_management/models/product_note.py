from odoo import _, api, fields, models

class ProductNote(models.Model):
    _name = "product.note"
    
    name = fields.Char(translate=True)
    product_ids = fields.One2many('product.product', 'product_note')
