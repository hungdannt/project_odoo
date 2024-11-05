from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    signature_image = fields.Image()
    registration_number = fields.Char()
