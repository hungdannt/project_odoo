
from odoo import api, models

from odoo.addons.zet_sale_management.models.foreign_amount import calcula_foreign_amount

class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _compute_taxes_for_single_line(self, base_line, handle_price_include=True, include_caba_tags=False, early_pay_discount_computation=None, early_pay_discount_percentage=None):
        to_update_vals, tax_values_list = super()._compute_taxes_for_single_line(base_line, handle_price_include,
                                                                                 include_caba_tags, early_pay_discount_computation, early_pay_discount_percentage)
        if self._context.get('foreign_tax_totals'):
            if to_update_vals.get('price_subtotal'):
                to_update_vals['price_subtotal'] = calcula_foreign_amount(to_update_vals['price_subtotal'], base_line['record'].conversion_rate)
            if to_update_vals.get('price_total'):
                to_update_vals['price_total'] = calcula_foreign_amount(to_update_vals['price_total'], base_line['record'].conversion_rate)
            for tax in tax_values_list:
                if tax.get('base_amount_currency'):
                    tax['base_amount_currency'] = calcula_foreign_amount(tax['base_amount_currency'], base_line['record'].conversion_rate)
                if tax.get('base_amount'):
                    tax['base_amount'] = calcula_foreign_amount(tax['base_amount'], base_line['record'].conversion_rate)
                if tax.get('tax_amount_currency'):
                    tax['tax_amount_currency'] = calcula_foreign_amount(tax['tax_amount_currency'], base_line['record'].conversion_rate)
                if tax.get('tax_amount'):
                    tax['tax_amount'] = calcula_foreign_amount(tax['tax_amount'], base_line['record'].conversion_rate)
        return to_update_vals, tax_values_list
