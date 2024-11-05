from datetime import datetime, timedelta

from odoo import Command, _, api, exceptions, fields, models
from odoo.addons.haverton_base.tools.datetime import (
    convert_date_to_user_lang_format,
    get_date_range_in_week,
)

from ..schemas import Defect, JobActivity, JobVariation
from ..utils import user as user_utils

CONFIRMED_BOOKING_STATUSES = {
    'confirmed': 'Confirmed',
}
DEFECT_REQUIRED_FIELDS = [
    'defect_type_id',
    'defect_description',
]


class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Activity/Defect/Variation'
    _inherit = ['project.task', 'abstract.uuid']

    job_status = fields.Char(
        string='Job Status', related='project_id.stage_id.name', store=True)
    is_active_workflow = fields.Boolean(
        related='project_id.stage_id.is_active_workflow')
    booking_status = fields.Selection([
        *CONFIRMED_BOOKING_STATUSES.items(),
        ('not_confirmed', 'Not Confirmed'),

    ], compute="compute_booking_status", store=True)
    booking_confirmed_on = fields.Datetime()
    total_defects = fields.Integer(
        string='Defects', compute="_compute_total_defects")
    booked_start_date = fields.Datetime(string='Booked Start', tracking=True)
    old_booked_start_date = fields.Datetime()
    forecasted_start_date = fields.Datetime(
        string='Forecasted Start')  # required with activity
    start_date = fields.Datetime(string='Start')
    days_until_completion = fields.Integer(
        string='Days Until Comp', compute='_compute_days_until_completion')
    days_remaining = fields.Integer(
        string='Ahead/Behind', compute='_compute_days_remaining')
    user_id = fields.Many2one(
        'res.users', help='The user who is responsible for the task'
    )
    comp = fields.Many2one('haverton.compliance', related="service_provider_id.compliance_id",
                           help='The status of the Service Provider, retrieved from Companion.')
    service_type = fields.Many2one('haverton.service.type')
    defect_type_id = fields.Many2one('haverton.service.type')
    job_activity_id = fields.Many2one('project.task', string='Job Activity', index=True,
                                      domain="['!', ('id', 'child_of', id)]", tracking=True)
    defect_ids = fields.One2many('project.task', 'job_activity_id', string="Defects",
                                 domain="[('haverton_task_type', '=', 'defect')]")
    haverton_defect_category_id = fields.Many2one(
        'haverton.defect.category', string='Defect Category')
    defect_details = fields.Text(string='Defect Detail')
    defect_action = fields.Text()
    defect_description = fields.Text()
    currency_id = fields.Many2one(
        'res.currency', string='Company Currency', default=lambda self: self.env.company.currency_id)
    defect_amount = fields.Monetary(
        string='Back Charge Amount', currency_field='currency_id')
    is_back_charge = fields.Boolean(default=False)
    work_day_duration = fields.Integer(string='Duration (in work days)')
    location_ids = fields.Many2many('haverton.location')
    is_auto_assign_service_provider = fields.Boolean(default=False)
    charge_to = fields.Many2one(
        'res.partner', domain="[('haverton_contact_type', '=', 'service_provider'), '|', ('company_id', '=?', company_id), "
                              "('company_id', '=', False)]")
    status = fields.Selection([
        ('normal', 'Normal'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
    ], compute='_compute_status')
    dashboard_activity_status = fields.Selection([
        ('due_activities', 'Due Activities'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ], compute='_compute_dashboard_activity_status')
    contract_no = fields.Char(string='Job Contract No',
                              related="project_id.contract_no")
    images_section = fields.One2many(
        'attachment.section', 'task_id', string="Images Section")
    haverton_task_type = fields.Selection([
        ('activity', 'Activity'),
        ('defect', 'Defect'),
        ('variation', 'Variation'),
    ], default='activity')
    haverton_activity_question_answer_ids = fields.One2many(
        'haverton.activity.question.answer', 'task_id')
    note = fields.Text('Note')
    attach_documents = fields.Many2many(
        'ir.attachment', 'variation_document_rel', string="Attach Documents")
    predecessor_ids = fields.Many2many(
        string='Predecessors',
        comodel_name='project.task',
        relation='task_predecessor_rel',
        column1='task_id',
        column2='predecessor_id')
    successor_ids = fields.Many2many(
        string='Successors',
        comodel_name='project.task',
        relation='task_predecessor_rel',
        column1='predecessor_id',
        column2='task_id')
    sequence_predecessors = fields.Json(
        string='Predecessors',
        compute='_compute_sequence_predecessors')
    sequence_successors = fields.Json(
        string='Successors',
        compute='_compute_sequence_successors')
    haverton_create_date = fields.Datetime(string='Created Date')

    # variation
    reference = fields.Char()
    invoice_number = fields.Char()
    reason_id = fields.Many2one(
        'haverton.code', domain="[('code_type', '=', 'variation_reason')]")
    approval_id = fields.Many2one(
        'haverton.code', domain="[('code_type', '=', 'variation_approval')]")
    create_by = fields.Char(string='Created By')
    approval_last_updated_by = fields.Char()
    reason_domain = fields.Char()
    reason_code = fields.Char()
    approval_domain = fields.Char()
    approval_code = fields.Char()
    haverton_service_uuid = fields.Char()
    inspection_id = fields.Many2one('survey.user_input')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    job_address = fields.Text(string='Job Address',
                              related='project_id.address_details')
    is_send_mail_create_defect = fields.Boolean()
    address_id = fields.Many2one(
        'haverton.address', related='project_id.address_id')
    date_deadline = fields.Datetime(string='Forecasted Completion')
    name = fields.Char(string='Name/Variation Summary')
    date_end = fields.Datetime(string='Completion')

    @property
    def single_activity_domain(self) -> list[tuple]:
        """
        Domain to get activities not in any variation.
        """
        return [
            ('haverton_task_type', '=', 'activity'),
            ('parent_id', '=', False),
        ]

    @property
    def haverton_updatable_fields(self):
        return set(Defect.model_fields.keys() | JobActivity.model_fields.keys() | JobVariation.model_fields.keys())

    @api.constrains('haverton_task_type', *DEFECT_REQUIRED_FIELDS)
    def _check_required_fields(self):
        for rec in self:
            if rec.haverton_task_type == 'defect':
                for fname in DEFECT_REQUIRED_FIELDS:
                    if getattr(rec, fname):
                        continue
                    raise exceptions.UserError(
                        _("%s is required in a defect." % fname)
                    )

    @api.depends('predecessor_ids')
    def _compute_sequence_predecessors(self):
        for rec in self:
            rec.sequence_predecessors = [
                i.sequence for i in rec.predecessor_ids]

    @api.depends('successor_ids')
    def _compute_sequence_successors(self):
        for rec in self:
            rec.sequence_successors = [i.sequence for i in rec.successor_ids]

    @api.depends('date_deadline')
    def _compute_days_until_completion(self):
        for rec in self:
            if rec.date_deadline:
                rec.days_until_completion = (
                    rec.date_deadline.date() - datetime.now().date()).days
            else:
                rec.days_until_completion = None

    @api.depends('date_deadline', 'project_id.date_start')
    def _compute_days_remaining(self):
        for rec in self:
            project_id = rec.project_id
            if rec.date_deadline and project_id and project_id.date_start:
                rec.days_remaining = (
                    rec.date_deadline.date() - project_id.date_start).days
            else:
                rec.days_remaining = None

    def _auto_init(self):
        super()._auto_init()
        # set old_booked_start_date for the existing records
        try:
            if not self._abstract:
                self.env.cr.execute("""
                    UPDATE %s SET old_booked_start_date = booked_start_date WHERE old_booked_start_date IS NULL;
                """ % self._table)
        except Exception:
            self.env.cr.rollback()

    @api.depends("defect_ids")
    def _compute_total_defects(self):
        for rec in self:
            rec.total_defects = len(rec.defect_ids)

    @api.depends('date_deadline', 'date_end')
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_end:
                rec.status = 'completed'
            elif rec.date_deadline and rec.date_deadline.date() < today:
                rec.status = 'overdue'
            else:
                # status is normal if date_deadline is not set or date_deadline has not been reached
                rec.status = 'normal'

    @api.depends('date_deadline')
    def _compute_dashboard_activity_status(self):
        today = fields.Date.today()
        dashboard_filter_date_start = self.env.context.get(
            "dashboard_filter_date_start", None
        )
        dashboard_filter_date_end = self.env.context.get(
            "dashboard_filter_date_end", None
        )
        if dashboard_filter_date_start and dashboard_filter_date_end:
            dt_start, dt_end = user_utils.get_period_datetime_range(
                dashboard_filter_date_start, dashboard_filter_date_end)
        else:
            dt_start = datetime.combine(today, datetime.min.time())
            dt_end = datetime.combine(today, datetime.max.time())
        for rec in self:
            rec.dashboard_activity_status = 'pending'
            if rec.date_deadline:
                if rec.date_deadline >= dt_start and rec.date_deadline <= dt_end:
                    rec.dashboard_activity_status = 'due_activities'
                elif rec.date_deadline < dt_start:
                    rec.dashboard_activity_status = 'overdue'

    def convert_defect_description_and_name(self, vals):
        if vals.get('defect_description') != str(vals.get('name')):
            if vals.get('defect_description'):
                vals['name'] = vals['defect_description']
            elif vals.get('name'):
                vals['defect_description'] = vals['name']
        return vals

    def prepare_creation_vals_list(self, vals_list):
        vals_list = super().prepare_creation_vals_list(vals_list)
        for vals in vals_list:
            project = self.env['project.project'].browse(
                vals.get('project_id'))
            if not vals.get('sequence') and project and not self.env.context.get('in_data_sync'):
                vals['sequence'] = project.get_latest_task_sequence(
                    vals.get('haverton_task_type')) + 1
            if vals.get('booked_start_date'):
                vals['old_booked_start_date'] = vals['booked_start_date']
            vals = self.convert_defect_description_and_name(vals)
        return vals_list

    def get_assigned_value_fields(self):
        res = super().get_assigned_value_fields()
        if self.create_uid and not self.create_by:
            res['create_by'] = self.create_uid.name or ' '
        return res

    @api.depends('booking_confirmed_on', 'booked_start_date')
    def compute_booking_status(self):
        for rec in self:
            if rec.booking_confirmed_on and rec.booked_start_date:
                rec.booking_status = 'confirmed'
            elif rec.booked_start_date:
                rec.booking_status = 'not_confirmed'
            else:
                rec.booking_status = False

    def create_attachment_section(self, attachment_section_vals, is_update=False):
        self.ensure_one()
        create_vals_list = []
        if is_update:
            current_section_uuid = set(self.images_section.mapped('uuid'))
            need_delete_uuid = current_section_uuid - set(obj.uuid for obj in attachment_section_vals if obj.uuid)
            self.env['attachment.section'].search([('uuid', 'in', list(need_delete_uuid))]).unlink()
        for section in attachment_section_vals:
            section_vals = {'task_id': self.id}
            if section.description:
                section_vals['description'] = section.description
            if section.attach_images:
                attachments = self.env['ir.attachment'].search([('uuid', 'in', section.attach_images)])
                if attachments:
                    section_vals['attach_images'] = [Command.set(attachments.ids)]
            if section.uuid:
                exist_section = self.env['attachment.section'].validate_by_uuid(section.uuid)
                exist_section.write(section_vals)
            else:
                create_vals_list.append(section_vals)
        if create_vals_list:
            self.env['attachment.section'].create(create_vals_list)

    def get_current_date(self, date=None):
        return convert_date_to_user_lang_format(date or datetime.now())

    def assign_fields_after_creation(self):
        super().assign_fields_after_creation()
        for rec in self:
            if not rec.company_id:
                rec.company_id = self.env.company

    def prepare_writing_vals(self, vals):
        vals = self.convert_defect_description_and_name(vals)
        current_user = self.env.user
        if vals.get('date_end') and current_user and not self.env.context.get('in_data_sync'):
            vals['user_id'] = current_user.id
        return vals

    def write(self, vals):
        vals = self.prepare_writing_vals(vals)
        res = super().write(vals)
        return res

    @property
    def days_until_task_start_reminder(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_job_management.days_until_task_start_reminder'
        ) or 2)  # default: 2 days

    def _get_upcoming_task_domain(self):
        dt_check = datetime.now() + timedelta(self.days_until_task_start_reminder)
        dt_check_start = dt_check.replace(
            hour=0, minute=0, second=0, microsecond=0)
        dt_check_end = dt_check_start + \
            timedelta(days=1) - timedelta(microseconds=1)
        return [('forecasted_start_date', '>=', dt_check_start), ('forecasted_start_date', '<=', dt_check_end), ('date_end', '=', False)]

    def remind_upcoming_tasks(self):
        upcoming_tasks = self.search(self._get_upcoming_task_domain())
        template = self.env.ref(
            'haverton_job_management.notification_template_task_reminder')
        if not template:
            return
        for record in upcoming_tasks:
            remaining_time_str = str(self.days_until_task_start_reminder) + \
                (' days' if self.days_until_task_start_reminder > 1 else ' day')
            template.send_notification(
                res_ids=[record.id],
                add_context={
                    'remaining_time': remaining_time_str
                },
                screen_type=record.haverton_task_type
            )

    @api.model
    def get_alive_activity_due_next_week_domain(self):
        date_now = datetime.today().date()
        date_start, date_end = get_date_range_in_week(
            date_now + timedelta(days=7))
        domain = [
            ('haverton_task_type', '=', 'activity'),
            ('date_end', '=', False),
            ('date_deadline', '>=', date_start),
            ('date_deadline', '<=', date_end),
        ]
        return domain
