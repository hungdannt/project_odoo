from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    job_number_ids = fields.Many2many('sale.order', string="Job Number")

    def _prepare_account_move_line(self):
        res = super()._prepare_account_move_line()
        res.update({
            'job_number_ids': [(6, 0, self.job_number_ids.ids)],
        })
        return res
