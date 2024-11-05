from datetime import datetime

from odoo import _, api, exceptions, fields, models
from odoo.addons.haverton_base.tools.datetime import convert_date_to_user_lang_format

from ..schemas import Job


class ProjectProject(models.Model):
    _name = 'project.project'
    _description = 'Haverton Job'
    _inherit = ['project.project', 'abstract.uuid']

    contract_no = fields.Char(required=True, help='Job Number')
    client_id = fields.Many2one('res.partner', domain="[('haverton_contact_type', '=', 'client'), '|', "
                                                      "('company_id', '=?', company_id),""('company_id', '=', False)]")
    client_name = fields.Char(related="client_id.name")
    est_date = fields.Datetime(string='Estimation Date',
                               required=True, help='Forecast Completion Date')
    overdue = fields.Integer(
        compute='_compute_overdue', help='The number of overdue days, calculated as Today - Forecast Completion Date.')
    contract_house_design = fields.Char()
    region_id = fields.Many2one(comodel_name='haverton.region')
    location_ids = fields.Many2many(comodel_name='haverton.location')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    contract_value_ex_gst = fields.Float(
        'Contract Value Ex GST', required=True)
    contract_value_inc_gst = fields.Float(
        'Contract Value Inc GST', required=True)
    contract_details = fields.Char(compute='_compute_contract_details')
    write_user_name = fields.Char(
        related='write_uid.name', store=True, help='The name of the user who last updated the record')
    total_activities = fields.Integer(compute='_compute_total_activities')
    total_defects = fields.Integer(compute='_compute_total_defects')
    total_variants = fields.Integer(compute='_compute_total_variants')
    supervisor_id = fields.Many2one('res.users')
    address_id = fields.Many2one('haverton.address')
    address = fields.Char(related='address_id.name')
    address_details = fields.Text(related='address_id.site_address')
    haverton_write_date = fields.Datetime(string='Haverton Last Updated On')
    document_directory_number = fields.Integer()
    is_completed_by_user = fields.Boolean(compute='_compute_is_completed_by_user')
    contract_start_on = fields.Datetime()
    contract_end_on = fields.Datetime()
    stage_id = fields.Many2one(string='Job Status')
    date_start = fields.Date(string='WF Start Date')

    @property
    def haverton_updatable_fields(self):
        return set(Job.model_fields.keys())

    @api.depends('task_ids', 'task_ids.date_end')
    def _compute_is_completed_by_user(self):
        for rec in self:
            rec.is_completed_by_user = rec.check_project_is_completed_by_users(
                [self.env.user]
            )

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for rec in self:
            rec.currency_id = main_company.currency_id.id

    @api.depends('est_date')
    def _compute_overdue(self):
        for rec in self:
            if rec.est_date:
                rec.overdue = (datetime.now().date() - rec.est_date.date()).days
            else:
                rec.overdue = None

    @api.depends('task_ids', 'task_ids.haverton_task_type')
    def _compute_total_activities(self):
        for rec in self:
            rec.total_activities = len(
                rec.task_ids.filtered_domain([('haverton_task_type', '=', 'activity')]))

    @api.depends('task_ids', 'task_ids.haverton_task_type')
    def _compute_total_defects(self):
        for rec in self:
            rec.total_defects = len(
                rec.task_ids.filtered_domain([('haverton_task_type', '=', 'defect')]))

    @api.depends('task_ids', 'task_ids.haverton_task_type')
    def _compute_total_variants(self):
        for rec in self:
            rec.total_variants = len(
                rec.task_ids.filtered_domain([('haverton_task_type', '=', 'variation')]))

    @api.depends('contract_start_on', 'contract_end_on')
    def _compute_contract_details(self):
        for rec in self:
            if not rec.contract_start_on:
                rec.contract_details = _('Contract has not started')
            else:
                rec.contract_details = _('Contract runs from %s to %s' % (
                    convert_date_to_user_lang_format(rec.contract_start_on),
                    convert_date_to_user_lang_format(rec.contract_end_on.date()) if rec.contract_end_on else '-'))

    def check_project_is_completed_by_users(self, users):
        self.ensure_one()
        domain = [
            ('haverton_task_type', 'in', ['activity', 'defect']),
            ('date_end', '=', False),
            ('user_id', 'in', [user.id for user in users]),
        ]
        domain.append(('user_id', 'in', [user.id for user in users]))
        not_completed_tasks = self.task_ids.filtered_domain(domain)
        return True if len(not_completed_tasks) == 0 else False
    
    def get_latest_task_sequence(self, haverton_task_type: str):
        self.ensure_one()
        if not haverton_task_type:
            raise exceptions.UserError(
                _("haverton_task_type is required.")
            )
        latest_rec = self.env['project.task'].search_read(
            [('project_id', '=', self.id), ('haverton_task_type', '=', haverton_task_type)],
            order="sequence desc", limit=1, fields=['sequence']
        )
        return latest_rec[0].get('sequence') if latest_rec else 0

    @api.model
    def _update_contract_no_and_name(self, value):
        if value.get('contract_no'):
            value['name'] = value['contract_no']
        if value.get('name'):
            value['contract_no'] = value['name']

    @api.model
    def create(self, value):
        self._update_contract_no_and_name(value)
        return super().create(value)

    def write(self, value):
        self._update_contract_no_and_name(value)
        return super().write(value)

    def get_service_provider(self, service_type_uuid):
        self.ensure_one()
        if not service_type_uuid:
            return False
        activities = self.task_ids.filtered(
            lambda task: task.service_type.uuid == service_type_uuid and task.haverton_task_type == 'activity')
        if activities:
            return activities[0].service_provider_id.id
        return False
