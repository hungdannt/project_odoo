from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    support_content = fields.Html(sanitize_style=True)
    logo_image = fields.Many2one('ir.attachment')
    report_logo = fields.Binary(string="Report logo")
