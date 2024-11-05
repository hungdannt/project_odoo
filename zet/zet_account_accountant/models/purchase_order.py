from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    classification_type_id = fields.Many2one('cost.classification.type', string="Type")
    invoice_ref_date = fields.Date(string='Invoice Reference Date')
    invoice_ref = fields.Text(string='Invoice Reference Number')
    vessel_name = fields.Text()
    bank_transfers_date = fields.Date()
    remarks = fields.Text()
    
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({
            'classification_type_id': self.classification_type_id.id,
            'invoice_ref_date': self.invoice_ref_date,
            'invoice_ref': self.invoice_ref,
            'vessel_name': self.vessel_name,
            'bank_transfers_date': self.bank_transfers_date,
            'remarks': self.remarks
        })
        return res

    def action_analyze(self):
        self.ensure_one()
        set_account_ids = set()
        for line in self.order_line:
            if line.analytic_distribution:
                ids = [int(key) for key in line.analytic_distribution.keys()]
                set_account_ids.update(ids)
        if not set_account_ids:
            raise UserError(_('Please add valid analytic distrubution in lines.'))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Analytic Account'),
            'view_mode': 'form',
            'res_model': 'select.analytic.wizard',
            'context': {
                'analytic_account_ids': list(set_account_ids),
                'default_analytic_account_ids': [(6, 0, list(set_account_ids))],
            },
            'target': 'new',
        }
