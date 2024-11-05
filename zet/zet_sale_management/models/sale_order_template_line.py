from odoo import fields, models

class SaleOrderTemplateLine(models.Model):
    _inherit = 'sale.order.template.line'

    is_sub_section = fields.Boolean()

    def _prepare_order_line_values(self):
        value = super()._prepare_order_line_values()
        value['is_sub_section'] = self.is_sub_section
        return value
