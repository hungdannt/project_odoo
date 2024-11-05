from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    signature_image = fields.Image()
