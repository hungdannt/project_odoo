from odoo import fields, models


class ProjectProjectStage(models.Model):
    _name = 'project.project.stage'
    _description = 'Job Status'
    _inherit = ['abstract.uuid', 'project.project.stage']
    _order = 'sequence'

    name = fields.Char(required=True)
    defect_status = fields.Boolean(default=False)
    system_code = fields.Char()
    is_active_workflow = fields.Boolean(default=False)
    sequence = fields.Integer()
    is_auto_recalculated_status = fields.Boolean(default=False)
    is_on_hold = fields.Boolean(default=False)
    haverton_create_date = fields.Datetime(string='Haverton Created On')
