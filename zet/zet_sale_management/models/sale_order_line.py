from odoo import api, fields, models
from datetime import datetime
from odoo.addons.zet_sale_management.models.foreign_amount import calcula_foreign_amount


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line', 'upload.attach.file', 'foreign.amount']

    attachment_ids = fields.Many2many('ir.attachment')
    is_sub_section = fields.Boolean()
    product_note = fields.Many2one('product.note')
    tmp_sequence = fields.Integer(related="sequence")
    voucher_reference = fields.Char()
    fixed_price = fields.Float(
        related='price_unit', readonly=False)
    foreign_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Foreign Currency",
        help="The optional other currency if it is a multi-currency entry.",
        related='order_id.foreign_currency_id'
    )
    foreign_price_subtotal = fields.Monetary(
        compute='_foreign_price_subtotal_and_total',
        string="Amount (Foreign)",
        currency_field='foreign_currency_id',
    )
    foreign_price_total = fields.Monetary(
        compute='_foreign_price_subtotal_and_total',
        string="Foreign Tax incl.",
        currency_field='foreign_currency_id',
    )
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        help="Price of products in Main currency",
        store=True, readonly=False, required=True, precompute=True)
    
    @api.depends('foreign_currency_id', 'price_subtotal', 'conversion_rate', 'price_total')
    def _foreign_price_subtotal_and_total(self):
        for rec in self:
            rec.foreign_price_subtotal = 0
            rec.foreign_price_total = 0
            if rec.conversion_rate:
                rec.foreign_price_subtotal = calcula_foreign_amount(rec.price_subtotal, rec.conversion_rate)
                rec.foreign_price_total = calcula_foreign_amount(rec.price_total, rec.conversion_rate)

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for rec in self:
            rec.conversion_rate = rec.order_id.conversion_rate or rec.pricelist_item_id.conversion_rate or rec.order_id.pricelist_id.conversion_rate or 0.0
            rec.foreign_price = rec.pricelist_item_id.foreign_price or 0
