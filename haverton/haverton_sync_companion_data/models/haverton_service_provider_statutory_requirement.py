from odoo import api, models

from ..companion.models import ServiceProviderStatutoryRequirement


class HavertonServiceProviderStatutoryRequirement(models.Model):
    _name = 'haverton.service.provider.statutory.requirement'
    _inherit = ['abstract.companion.data.sync',
                'haverton.service.provider.statutory.requirement']

    @property
    def companion_model(self):
        return ServiceProviderStatutoryRequirement

    @property
    def companion_primary_column_name(self):
        return 'ServiceProviderID'

    def check_record_existed(self, record: object):
        return not not self.browse_by_primary_fields(
            service_provider_id=getattr(record, 'ServiceProviderID'),
            statutory_requirement_domain_number=getattr(record, 'StatutoryRequirementDomainNumber'),
            statutory_requirement_code_number=getattr(record, 'StatutoryRequirementCodeNumber'),
        )

    @api.model
    def companion_field_mapping(self):
        return {
            'ServiceProviderID': 'service_provider_id',
            'StatutoryRequirementDomainNumber': 'statutory_requirement_domain_number',
            'StatutoryRequirementCodeNumber': 'statutory_requirement_code_number',
            'CreationTime': 'haverton_create_date',
            'ExpiryDate': 'expiry_date',
            'ExpiryDateLastUpdatedTime': 'expiry_date_last_updated_time',
        }

    def companion_primary_columns_mapping(self):
        return {
            'ServiceProviderID': 'service_provider_id',
            'StatutoryRequirementDomainNumber': 'statutory_requirement_domain_number',
            'StatutoryRequirementCodeNumber': 'statutory_requirement_code_number',
        }
