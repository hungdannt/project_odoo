from odoo import  models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    is_fda = fields.Boolean()

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['is_fda'] = "s.is_fda"
        return res
