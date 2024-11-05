from odoo import api, models

from ..companion.models import Region


class HavertonRegion(models.Model):
    _name = 'haverton.region'
    _inherit = ['abstract.companion.data.sync', 'haverton.region']

    @property
    def companion_model(self):
        return Region

    @property
    def companion_primary_column_name(self):
        return 'RegionID'

    @property
    def companion_parent_column_name(self):
        return 'ParentRegionID'

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'Description': 'description',
            'IsDefaultJobRegion': 'is_default_job_region',
            'IsDefaultServiceProviderRegion': 'is_default_service_provider_region',
            'Active': 'active',
        }
