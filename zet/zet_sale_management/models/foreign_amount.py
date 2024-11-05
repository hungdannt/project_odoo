from odoo import api, fields, models, _
from odoo.http import request


def calcula_foreign_amount(amount, conversion_rate):
    if not conversion_rate or not amount:
        return 0
    return amount * conversion_rate


class ForeignAmount(models.AbstractModel):
    _name = "foreign.amount"
    _description = "Foreign Amount"
    
    onchange_fixed_price_or_conversion_rate = fields.Boolean()
    onchange_foreign_price = fields.Boolean()

    foreign_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Foreign Currency",
        help="The optional other currency if it is a multi-currency entry.",
    )
    foreign_price = fields.Monetary(
        currency_field='foreign_currency_id',
        help="Price of products in Foreign currency.",
    )
    fixed_price = fields.Float()
    conversion_rate = fields.Float(help="Conversion rate between Main currency & Foreign Currency", digits=(16, 8))

    @api.onchange('foreign_price')
    def _onchange_foreign_price(self):
        for rec in self:
            if not rec.onchange_fixed_price_or_conversion_rate:
                rec.fixed_price = rec.foreign_price * rec.conversion_rate
                if 'price_unit' in rec._fields and rec.fixed_price != rec.price_unit:
                    rec.price_unit = rec.fixed_price
                rec.onchange_foreign_price = True
            else:
                rec.onchange_fixed_price_or_conversion_rate = False

    @api.onchange('conversion_rate', 'fixed_price')
    def _onchange_fixed_price_or_conversion_rate(self):
        for rec in self:
            if not rec.onchange_foreign_price:
                rec.foreign_price = calcula_foreign_amount(rec.fixed_price, rec.conversion_rate) or 0
                rec.onchange_fixed_price_or_conversion_rate = True
            else:
                rec.onchange_foreign_price = False

