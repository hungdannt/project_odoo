from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    order_line_ids = fields.Many2many('sale.order.line')
    sale_order_ids = fields.Many2many(
        'sale.order', compute="_compute_sale_order_ids", store=True)

    @api.depends('order_line_ids')
    def _compute_sale_order_ids(self):
        for rec in self:
            rec.sale_order_ids = rec.order_line_ids.order_id

