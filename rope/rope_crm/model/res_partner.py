# coding: utf-8
from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_id = fields.Many2one('res.company', 'Company', index=True, request=True)

    @api.model
    def create(self, value):
        res = super().create(value)
        if not self._context.get('from_create_company'):
            res.company_id = self.env.company
        return res
