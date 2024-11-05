from odoo import _, api, fields, models

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    foreign_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Foreign Currency",
        help="The optional other currency if it is a multi-currency entry.",
        default=lambda self:self.env.ref('base.USD')
    )
    hide_exchange_price = fields.Boolean(compute='_compute_hide_exchange_price')
    customer_ids = fields.Many2many('res.partner')
    conversion_rate = fields.Float(digits=(16, 8))

    @api.depends('currency_id', 'foreign_currency_id')
    def _compute_hide_exchange_price(self):
        for rec in self:
            rec.hide_exchange_price = rec.currency_id == rec.foreign_currency_id or not rec.foreign_currency_id
    
    @api.onchange('foreign_currency_id', 'currency_id')
    def _onchange_currency_or_foreign_currency(self):
        self.conversion_rate = self.foreign_currency_id.rate / self.currency_id.rate if self.currency_id.rate != 0 else 0.0

    def update_all_conversion_rate(self):
        for rec in self:
            rec.item_ids.write({
                'conversion_rate': rec.conversion_rate
            })
            rec.item_ids._onchange_fixed_price_or_conversion_rate()
