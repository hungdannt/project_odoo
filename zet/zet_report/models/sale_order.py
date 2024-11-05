from odoo import api, models, fields, _, SUPERUSER_ID


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'attachment.pdf']

    attachment_ids = fields.Many2many('ir.attachment', compute="_compute_attachment_ids")
    digital_ver = fields.Boolean(default=True)
    
    @api.depends('order_line.attachment_ids')
    def _compute_attachment_ids(self):
        for order in self:
            order.attachment_ids = order.order_line.attachment_ids

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            if record.state in ('draft', 'sent', 'cancel'):
                record.type_name = _("Quotation")
            else:
                record.type_name = "FDA #" if record.is_fda else "PDA #"
