from odoo import fields, models


class HavertonServiceProviderStatutoryRequirement(models.Model):
    _name = 'haverton.service.provider.statutory.requirement'
    _description = """
        Represent for ServiceProviderStatutoryRequirement table in Haverton.
        Used to compute compliance_id of the res.partner records
    """
    _inherit = 'abstract.uuid'

    service_provider_id = fields.Many2one('res.partner', required=True)
    statutory_requirement_domain_number = fields.Integer(required=True)
    statutory_requirement_code_number = fields.Integer(required=True)
    haverton_create_date = fields.Datetime(string='Haverton Created On')
    expiry_date = fields.Datetime()
    expiry_date_last_updated_time = fields.Datetime()

    _sql_constraints = [
        (
            "primary_key_uniq",
            "unique(service_provider_id, statutory_requirement_domain_number, statutory_requirement_code_number)",
            "This HavertonServiceProviderStatutoryRequirement already exists."
        )
    ]

    def browse_by_primary_fields(self, **kwargs):
        service_provider_id = kwargs.get('service_provider_id')
        service_provider_id = self.env['res.partner'].browse_by_haverton_uuid(
            service_provider_id)
        domain_number = kwargs.get('statutory_requirement_domain_number')
        code_number = kwargs.get('statutory_requirement_code_number')
        if any([
            not service_provider_id,
            not domain_number,
            not code_number,
        ]):
            return self
        return self.sudo().search([
            ('service_provider_id', '=', service_provider_id.id),
            ('statutory_requirement_domain_number', '=', domain_number),
            ('statutory_requirement_code_number', '=', code_number)
        ], limit=1)
