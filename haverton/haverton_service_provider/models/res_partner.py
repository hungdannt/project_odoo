# -*- coding: utf-8 -*-
import re
from datetime import datetime

from odoo import _, api, exceptions, fields, models

from ..schemas import ServiceProvider


class ResPartner(models.Model):
    _name = 'res.partner'
    _description = 'Service Provider'
    _inherit = ['res.partner', 'abstract.uuid']

    haverton_contact_type = fields.Selection([
        ('person', 'Person'),
        ('service_provider', 'Service Provider'),
        ('client', 'Client'),
    ])
    preferred_name = fields.Char()
    entity_code = fields.Char(help='The short name of a service provider')
    task_ids = fields.One2many(
        comodel_name='project.task', inverse_name='service_provider_id')
    region_ids = fields.Many2many(comodel_name='haverton.region')
    service_type_ids = fields.Many2many(comodel_name='haverton.service.type')
    compliance_id = fields.Many2one(
        'haverton.compliance', compute='_compute_compliance_id')
    work_category_ids = fields.Many2many(comodel_name='haverton.work.category')
    abn = fields.Char(string='ABN', size=14,
                      help='The Australian Business Number (ABN) is a unique 11-digit identifier.')
    url = fields.Char(string='URL')
    wr_preference_id = fields.Many2one(
        comodel_name='haverton.wr.preference', string='WR Preference')
    is_primary = fields.Boolean(default=False)
    is_secondary = fields.Boolean(default=False)
    address_id = fields.Many2one('haverton.address')
    formatted_address = fields.Text(
        related='address_id.site_address', string='Address')
    haverton_first_name = fields.Char()
    haverton_middle_name = fields.Char()
    haverton_last_name = fields.Char()
    override_requirements = fields.Integer()
    statutory_requirement_ids = fields.One2many(
        'haverton.service.provider.statutory.requirement', 'service_provider_id')
    personal_phone = fields.Char()
    personal_mobile = fields.Char()
    personal_email = fields.Char()
    phone = fields.Char(string='Phone Number')
    child_ids = fields.One2many(string='Contact List')
    name = fields.Char(string='Entity Name')

    @property
    def haverton_updatable_fields(self):
        return set(ServiceProvider.model_fields.keys())

    def get_compliance_id(self):
        """
        The data are in the table ServiceProviderStatutoryRequirement
        For now just use this rule, we may need to change it later

        1) If the Service Provider has no expired documents -> Compliances
        2) If the service provider has No documents at all : mark this SP as complied for now but the exact rule will depend on the service type, some service type required documents, some doesn't
        3) If the SP has expired documents -> non complied
        4) if the SP has expired documents but Overrided is ticked -> Partially complied.

        Other rules:
        5) if exist least 1 overriden uncollected document -> Partially complied.
        6) if exist least 1 uncollected document and not override -> Non-complied.
        """
        self.ensure_one()
        expired_statutory_requirement_ids = self.statutory_requirement_ids.filtered_domain([
            ('expiry_date', '<', datetime.now())
        ])
        uncollected_statutory_requirement_ids = self.statutory_requirement_ids.filtered_domain([
            ('expiry_date', '=', False)
        ])
        if len(expired_statutory_requirement_ids) == 0 and len(uncollected_statutory_requirement_ids) == 0:
            return self.env.ref('haverton_base.haverton_compliance_fully_complied')
        if not self.override_requirements:
            return self.env.ref('haverton_base.haverton_compliance_non_complied')
        return self.env.ref('haverton_base.haverton_compliance_partially_complied')

    @api.depends('override_requirements', 'statutory_requirement_ids', 'statutory_requirement_ids.expiry_date')
    def _compute_compliance_id(self):
        for rec in self:
            rec.compliance_id = rec.get_compliance_id()

    def _avatar_get_placeholder_path(self):
        if self.is_company:
            return "haverton_service_provider/static/img/company.svg"
        else:
            return "haverton_service_provider/static/img/invidual.svg"

    @api.constrains('abn')
    def _check_abn(self):
        for rec in self:
            if rec.abn and not re.fullmatch(r'\d{11}', rec.abn.replace(' ', '')):
                raise exceptions.UserError(
                    _('ABN must be a 11-digit identifier.'))

    def write(self, vals):
        if vals.get('is_primary'):
            self.parent_id.child_ids.filtered_domain(
                [('id', '!=', self.id), ('is_primary', '=', True)]).is_primary = False
        return super().write(vals)
