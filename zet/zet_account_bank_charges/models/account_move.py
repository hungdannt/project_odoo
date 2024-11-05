from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    bankcharge_id = fields.Many2one('account.payment')

    def button_open_payment(self):
        self.ensure_one()
        if self.bankcharge_id:
            return {
                'name': _("Payment"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'context': {'create': False},
                'view_mode': 'form',
                'res_id': self.bankcharge_id.id,
            }
