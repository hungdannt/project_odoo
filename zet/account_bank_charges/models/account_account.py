from odoo import fields, models


class AccountAccount(models.Model):
    """Added custom field account_account to add the bank charges"""
    _inherit = "account.account"

    bank_charge = fields.Monetary(currency_field='currency_id',
                                  string="Bank Charge",
                                  help="Bank charge amount")
