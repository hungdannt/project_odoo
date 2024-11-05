from odoo import fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    show_on_mobile_service_provider_detail = fields.Boolean(default=True)
