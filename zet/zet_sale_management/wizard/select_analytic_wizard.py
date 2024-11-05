from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SelectAnalyticWizard(models.TransientModel):
    _name = 'select.analytic.wizard'

    analytic_account_ids = fields.Many2many(
        'account.analytic.account', string='Analytic Accounts')

    def action_confirm(self):
        self.ensure_one()
        if not self.analytic_account_ids:
            raise UserError(_('Please choose analytic account'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Analytic Item'),
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'domain': [('auto_account_id', 'in', self.analytic_account_ids.ids)],
            'context': {'group_by': 'customer_id'}
        }
