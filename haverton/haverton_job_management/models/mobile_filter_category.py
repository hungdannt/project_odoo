from odoo import api, fields, models


class MobileFilterCategory(models.Model):
    _inherit = "mobile.filter.category"

    screen_type = fields.Selection(
        selection_add=[
            ("dashboard_activities", "Dashboard Activity"),
            ("todo_activities", "Todo Activity"),
            ('todo_defects', 'Todo Defect'),
            ('todo_variations', 'Todo Variation'),
            ('job_activities', 'Job Activity')
        ]
    )
