from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    has_limit = fields.Boolean(
        string="Has Limit", config_parameter='zet_sale_management.has_limit')
    number_of_lines_limit = fields.Integer(
        string="Number of Lines Limit", config_parameter='zet_sale_management.number_of_lines_limit')
    capacity_limit = fields.Integer(
        string="Capacity Limit", config_parameter='zet_sale_management.capacity_limit')
