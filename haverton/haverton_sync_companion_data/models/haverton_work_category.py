from odoo import api, models

from ..companion.models import WorkCategory


class HavertonWorkCategory(models.Model):
    _name = 'haverton.work.category'
    _inherit = ['abstract.companion.data.sync', 'haverton.work.category']

    @property
    def companion_model(self):
        return WorkCategory

    @property
    def companion_primary_column_name(self):
        return 'WorkCategoryID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Description': 'description',
        }
