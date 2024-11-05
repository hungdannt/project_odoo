from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_duplicate_record = fields.Boolean(default=False)

    def write(self, vals):
        if 'is_duplicate_record' not in vals:
            vals['is_duplicate_record'] = False
        return super().write(vals)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super().copy(default=default)
        res.is_duplicate_record = True
        return res

    def check_is_duplicate_record(self):
        self.ensure_one()
        return self.is_duplicate_record
