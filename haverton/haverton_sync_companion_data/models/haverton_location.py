from odoo import api, models

from ..companion.models import Location


class HavertonLocation(models.Model):
    _name = 'haverton.location'
    _inherit = ['abstract.companion.data.sync', 'haverton.location']

    @property
    def companion_model(self):
        return Location

    @property
    def companion_primary_column_name(self):
        return 'LocationID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Name': 'name',
            'Sequence': 'sequence',
            'IsActive': 'haverton_active',
        }
