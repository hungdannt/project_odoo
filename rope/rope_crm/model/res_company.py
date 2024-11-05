from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, values):
        self = self.with_context(from_create_company=True)
        res = super().create(values)
        return res


