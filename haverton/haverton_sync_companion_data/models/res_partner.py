import json

from odoo import api, models
from sqlalchemy import text

from ..companion.models import (
    Client,
    Person,
    ServiceProvider,
    ServiceProviderRegion,
    ServiceProviderServiceType,
)

HAVERTON_TABLE_CONTACT_TYPE_MAPPING = {
    'ServiceProvider': {'type': 'service_provider', 'haverton_column': 'ServiceProviderID'},
    'Person': {'type': 'person', 'haverton_column': 'PersonID'},
    'Client': {'type': 'client', 'haverton_column': 'ClientID'}
}

class HavertonResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['abstract.companion.data.sync', 'res.partner']

    @property
    def companion_primary_column_name(self):
        return 'ServiceProviderID'

    @property
    def companion_parent_column_name(self):
        return 'ParentID'

    @property
    def companion_model(self):
        return ServiceProvider

    def get_wr_preference(self, work_release_notification_preference):
        wr_preference = self.env.ref(
            'haverton_base.haverton_wr_preference_use_global_pre')
        match work_release_notification_preference:
            case 0:
                wr_preference = self.env.ref(
                    'haverton_base.haverton_wr_preference_email_wr')
            case 1:
                wr_preference = self.env.ref(
                    'haverton_base.haverton_wr_preference_email_linked_wr')
            case 2:
                wr_preference = self.env.ref(
                    'haverton_base.haverton_wr_preference_sms_wr')
            case 3:
                wr_preference = self.env.ref(
                    'haverton_base.haverton_wr_preference_sms_linked_wr')
            case 4:
                wr_preference = self.env.ref(
                    'haverton_base.haverton_wr_preference_sms_email_er')
            case 5:
                wr_preference = self.env.ref(
                    'haverton_base.haverton_wr_preference_sms_email_linked_wr')
        return wr_preference

    def _prepare_sync_companion_data(self, companion_data, session):
        vals_list = super()._prepare_sync_companion_data(companion_data, session)
        for vals in vals_list:
            if vals.get('haverton_contact_type') != 'service_provider':
                continue
            self._prepare_many2many_field(
                session, vals, 'haverton.service.type', ServiceProviderServiceType, 'service_type_ids', 'ServiceTypeID')
            self._prepare_many2many_field(
                session, vals, 'haverton.region', ServiceProviderRegion, 'region_ids', 'RegionID')
        return vals_list

    def _action_sync_companion_data_to_odoo(self, companion_data, session):
        vals_list = self._prepare_sync_companion_data(companion_data, session)
        new_records = self._insert_sync_companion_data(vals_list)
        if new_records:
            new_records._link_parent_id(companion_data)
        return new_records

    def _sync_companion_data(self, session):
        self = self.sudo().with_context(is_create=True)
        self._sync_companion_data_with_batch_size(
            session, ServiceProvider, ServiceProvider.ServiceProviderID, self._action_sync_companion_data_to_odoo)
        self._sync_companion_data_with_batch_size(
            session, Client, Client.ServiceProviderID, self._action_sync_companion_data_to_odoo)
        self._sync_companion_data_with_batch_size(
            session, Person, Person.ServiceProviderID, self._action_sync_companion_data_to_odoo)

    @api.model
    def companion_field_mapping(self):
        haverton_primary_field = HAVERTON_TABLE_CONTACT_TYPE_MAPPING.get(self.env.context.get('table_name'), {}).get(
            'haverton_column', self.companion_primary_column_name)
        return {
            haverton_primary_field: 'haverton_uuid',
            "OrganisationName": "name",
            "OrganisationTradingAsName": "preferred_name",
            "EntityCode": "entity_code",
            "ABN": "abn",
            "WorkUrl": "url",
            "IsPrimaryContact": "is_primary",
            "IsSecondaryContact": "is_secondary",
            "WorkAddressID": "address_id",
            "WorkPhone": "phone",
            "WorkMobile": "mobile",
            "WorkEmail": "email",
            "PersonalPhone": "personal_phone",
            "PersonalMobile": "personal_mobile",
            "PersonalEmail": "personal_email",
            "Active": "active",
            "WorkReleaseNotificationPreference": "wr_preference_id",
            "FirstName": "haverton_first_name",
            "MiddleNames": "haverton_middle_name",
            "LastName": "haverton_last_name",
            "HavertonContactType": "haverton_contact_type",
            "ParentID": "parent_id",
            "OverrideRequirements": "override_requirements",
            "JobDescription": "function",
        }

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        res = super(HavertonResPartner, self).prepare_companion_values(list_values,  sql_session)
        table_name = self.env.context.get('table_name')
        for value in res:
            if table_name == 'Person':
                value['name'] = ' '.join(filter(None, [value.get('haverton_first_name'), value.get('haverton_middle_name'), value.get('haverton_last_name')]))
            if self.env.context.get('is_create', False):
                if table_name:
                    value['haverton_contact_type'] = HAVERTON_TABLE_CONTACT_TYPE_MAPPING.get(table_name).get('type')
                if value.get('haverton_contact_type') == 'service_provider':
                    value['is_company'] = True
                if not value.get('preferred_name', False) and value.get('name', False):
                    value['preferred_name'] = value['name']
            if 'wr_preference_id' in value:
                wr_preference = self.get_wr_preference(value['wr_preference_id'])
                value['wr_preference_id'] = wr_preference.id if wr_preference else False

        return res
