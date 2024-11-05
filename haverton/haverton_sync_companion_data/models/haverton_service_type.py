from odoo import api, models

from ..companion.models import ServiceType


class HavertonServiceType(models.Model):
    _name = 'haverton.service.type'
    _inherit = ['abstract.companion.data.sync', 'haverton.service.type']

    @property
    def companion_model(self):
        return ServiceType

    @property
    def companion_primary_column_name(self):
        return 'ServiceTypeID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Description': 'description',
            'SystemCode': 'system_code',
            'WorkCategoryID': 'work_category_id',
        }
