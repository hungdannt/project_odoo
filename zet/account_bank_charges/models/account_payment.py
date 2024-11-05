from odoo import fields, models


class AccountPayment(models.Model):
    """Added custom field bank_charges to add the extra charges"""
    _inherit = "account.payment"

    bank_charges = fields.Monetary(currency_field='currency_id',
                                   string="Bank Charges",
                                   help="Bank charge amount")

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        """Adding bank charges in move line"""
        res = super(AccountPayment, self)._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals, force_balance=force_balance)
        if self.bank_charges:
            # Compute default label in journal items for bank charges.
            liquidity_line_name = ''.join(
                x[1] for x in self._get_liquidity_aml_display_name_list())
            bank_charges_line_name = liquidity_line_name.replace(
                str(("{:,}".format(self.amount))),
                str(self.bank_charges))
            move = self.env['account.move'].create(
                self._get_value_create_invoice_from_back_charges(bank_charges_line_name))
            move.action_post()
        return res

    def _get_value_create_invoice_from_back_charges(self, bank_charges_line_name):
        return {
            'journal_id': self.journal_id.id,
            'move_type': 'entry',
            'partner_id': self.partner_id.id,
            'line_ids': [
                (0, 0, {
                    'name': bank_charges_line_name,
                    'partner_id': self.partner_id.id,
                    'journal_id': self.journal_id.id,
                    'account_id': self.journal_id.account_id.id,
                    'debit': self.bank_charges,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': bank_charges_line_name,
                    'partner_id': self.partner_id.id,
                    'journal_id': self.journal_id.id,
                    'account_id': self.journal_id.default_account_id.id,
                    'debit': 0.0,
                    'credit': self.bank_charges,
                }),
            ],
        }
