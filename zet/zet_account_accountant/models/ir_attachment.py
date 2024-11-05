from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'


    account_move_line_ids = fields.Many2many('account.move.line')
    account_move_ids = fields.Many2many(
        'account.move', compute="_compute_account_move_ids", store=True)

    @api.depends('account_move_line_ids')
    def _compute_account_move_ids(self):
        for rec in self:
            rec.account_move_ids = rec.account_move_line_ids.move_id

