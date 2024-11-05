from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    support_content = fields.Html(
        related='company_id.support_content', readonly=False)
    api_debug = fields.Boolean(
        config_parameter='haverton_base.api_debug')
    logo_image = fields.Many2one(
        'ir.attachment', related='company_id.logo_image', readonly=False)
