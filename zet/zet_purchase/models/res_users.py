from odoo import models, fields


class ResUser(models.Model):
    _inherit = 'res.users'

    security_ids = fields.Many2many(
        'res.partner.security', string='Security', related="partner_id.security_ids", readonly=False)
