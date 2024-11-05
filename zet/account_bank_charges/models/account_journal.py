from odoo import fields, models


class AccountJournal(models.Model):
    """Added custom field default_bank_charges_account_id to
    account.journal model"""
    _inherit = 'account.journal'

    account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False,
        ondelete='restrict',
        string='Default Bank Charges Account',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id),]",
        help="The default bank charges account")
