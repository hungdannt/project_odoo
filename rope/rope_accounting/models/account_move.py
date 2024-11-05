from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    billing_bank_id = fields.Many2one('account.move.bank', string='Billing Bank')
