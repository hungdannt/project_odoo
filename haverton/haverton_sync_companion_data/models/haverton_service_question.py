from odoo import api, models

from ..companion.models import ServiceQuestion


class HavertonServiceQuestion(models.Model):
    _name = 'haverton.service.question'
    _inherit = ['abstract.companion.data.sync', 'haverton.service.question']

    @property
    def companion_model(self):
        return ServiceQuestion

    @property
    def companion_primary_column_name(self):
        return 'QuestionID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Question': 'question',
            'Sequence': 'sequence',
        }
