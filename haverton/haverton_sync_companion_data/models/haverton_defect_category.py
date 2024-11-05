from odoo import api, models

from ..companion.models import DefectCategory


class HavertonDefectCategory(models.Model):
    _name = 'haverton.defect.category'
    _inherit = ['abstract.companion.data.sync', 'haverton.defect.category']

    @property
    def companion_model(self):
        return DefectCategory

    @property
    def companion_primary_column_name(self):
        return 'DefectCategoryID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Name': 'name',
            'Type': 'category_type',
            'IsActive': 'active',
            'IsDefaultNew': 'is_default_new',
            'IsDefaultFromActivity': 'is_default_from_activity',
        }
