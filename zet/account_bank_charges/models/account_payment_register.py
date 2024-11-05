from odoo import fields, models


class AccountPaymentRegister(models.TransientModel):
    """Added custom field bank_charges to add the extra charges"""
    _inherit = 'account.payment.register'

    bank_charges = fields.Monetary(currency_field='currency_id',
                                   related="journal_id.account_id.bank_charge",
                                   string="Bank Charges",
                                   readonly=False,
                                   help="Bank charge amount")

    def _create_payment_vals_from_wizard(self, batch_result):
        """Create payment using values received from wizard."""
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['bank_charges'] = self.bank_charges
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        """Create payment using values received from wizard."""
        res = super(AccountPaymentRegister,
                    self)._create_payment_vals_from_batch(batch_result)
        res['bank_charges'] = self.bank_charges
        return res
