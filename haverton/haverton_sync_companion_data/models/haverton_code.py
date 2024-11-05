from odoo import api, models

from ..companion.models import Code


class HavertonCode(models.Model):
    _name = 'haverton.code'
    _inherit = ['abstract.companion.data.sync', 'haverton.code']

    @property
    def companion_model(self):
        return Code

    def check_record_existed(self, record: object):
        return len(self.browse_by_domain_and_code_number(domain=getattr(record, 'DomainNumber'), code=getattr(record, 'CodeNumber'))) > 0

    def get_code_type(self, domain_number):
        code_type = None
        haverton_code_domain_approval = int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.haverton_code_domain_approval'
        ) or 5)
        haverton_code_domain_reason = int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.haverton_code_domain_reason'
        ) or 6)
        if domain_number == haverton_code_domain_approval:
            code_type = 'variation_approval'
        elif domain_number == haverton_code_domain_reason:
            code_type = 'variation_reason'
        return code_type

    @api.model
    def companion_field_mapping(self):
        return {
            'CodeNumber': 'code_number',
            'DomainNumber': 'domain_number',
            'Name': 'name'
        }

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        res = super(HavertonCode, self).prepare_companion_values(
            list_values,  sql_session)
        for value in res:
            if 'domain_number' in value:
                value['code_type'] = self.get_code_type(value['domain_number'])
        return res
