from odoo import api, models

from ..companion.models import WorkflowStatus


class ProjectProjectStage(models.Model):
    _name = 'project.project.stage'
    _inherit = ['abstract.companion.data.sync', 'project.project.stage']

    @property
    def companion_model(self):
        return WorkflowStatus

    @property
    def companion_primary_column_name(self):
        return 'WorkflowStatusID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Name': 'name',
            'DefectStatus': 'defect_status',
            'SystemCode': 'system_code',
            'IsActiveWorkflow': 'is_active_workflow',
            'Sequence': 'sequence',
            'IsAutoRecalculatedStatus': 'is_auto_recalculated_status',
            'IsOnHold': 'is_on_hold',
            'CreatedOnUTC': 'haverton_create_date',
            'IsActive': 'active',
        }
