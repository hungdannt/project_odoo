from odoo import  models, api, fields


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'attachment.pdf']

    attachment_ids = fields.Many2many('ir.attachment', compute="_compute_attachment_ids")
    digital_ver = fields.Boolean(default=True)
    
    @api.depends('invoice_line_ids.attachment_ids', 'invoice_line_ids')
    def _compute_attachment_ids(self):
        for invoice in self:
            invoice.attachment_ids = invoice.invoice_line_ids.attachment_ids
