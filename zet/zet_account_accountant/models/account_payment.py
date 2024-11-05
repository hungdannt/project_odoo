from odoo import  models, fields, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    paid_by = fields.Text()
