from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_default_taxes(self, amount, type):
        return self.env['account.tax'].sudo().search([('amount', '=', amount), ('type_tax_use', '=', type), ('company_id', '=', self.company_id.id)], limit=1)

    @api.onchange('product_id')
    def product_id_change(self):
        super().product_id_change()
        self.tax_id = self._get_default_taxes(10.0, 'sale')
