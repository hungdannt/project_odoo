from odoo import api, fields, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    last_message = fields.Many2one(
        'mail.message', string='Message', compute="_compute_message")

    @api.depends('message_ids')
    def _compute_message(self):
        for rec in self:
            rec.last_message = False
            message_ids = rec.message_ids.filtered_domain(
                [('is_companion_message', '=', True)]).sorted('date')
            if message_ids:
                rec.last_message = message_ids[-1]
