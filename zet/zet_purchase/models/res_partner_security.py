from odoo import models, fields, api


class ResPartnerSecurity(models.Model):
    _name = 'res.partner.security'
    _inherit = 'res.partner.category'

    parent_id = fields.Many2one(
        'res.partner.security', string='Parent Category', index=True, ondelete='cascade')
    child_ids = fields.One2many(
        'res.partner.security', 'parent_id', string='Child Departments')
