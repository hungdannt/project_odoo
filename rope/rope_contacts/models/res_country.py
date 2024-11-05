from odoo import api, models, fields, _


class Country(models.Model):
    _inherit = 'res.country'
    _order = 'numerical_order asc, name'

    numerical_order = fields.Integer(string="Numerical Order", compute='_compute_numerical_order', store=True)

    @api.depends('code')
    def _compute_numerical_order(self):
        for rec in self:
            rec.numerical_order = 1 if rec.code == 'JP' else 2
