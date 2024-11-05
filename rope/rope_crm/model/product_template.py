from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    company_id = fields.Many2one('res.company', 'Company',  index=True, request=True, default=lambda self: self.env.company)