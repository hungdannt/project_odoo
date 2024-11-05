from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'voucher_reference': self.voucher_reference,
            'is_sub_section': self.is_sub_section,
            'foreign_currency_id': self.foreign_currency_id,
            'foreign_price': self.foreign_price,  # Corrected from foreign_currency_id to foreign_price
            'fixed_price': self.fixed_price,      # Corrected from foreign_currency_id to fixed_price
            'conversion_rate': self.conversion_rate,
            'attachment_ids': self.attachment_ids,
        })
        return res
