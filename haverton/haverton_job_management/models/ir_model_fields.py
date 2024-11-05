from odoo import fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    show_on_mobile_defect_detail = fields.Boolean(default=True)
    show_on_mobile_activity_detail = fields.Boolean(default=True)
    show_on_mobile_variation_detail = fields.Boolean(default=True)
    show_on_mobile_job_detail = fields.Boolean(default=True)
