from odoo import _, api, fields, models
from odoo.exceptions import UserError


class InspectionWizard(models.TransientModel):
    _name = "inspection.wizard"
    _description = "Expense Refuse Reason Wizard"

    survey_id = fields.Many2one('survey.survey', string="Inspection")
    project_id = fields.Many2one("project.project", string="Job", domain="[('stage_id.is_active_workflow', '=', True)]")
    task_id = fields.Many2one('project.task', string="Activity")
    task_id_domain = fields.Binary(compute="_compute_task_id_domain_domain")

    @api.depends('survey_id', 'task_id', 'project_id')
    def _compute_task_id_domain_domain(self):
        for rec in self:
            domain = [('haverton_task_type', '=', 'activity'), ('project_id', '=', rec.project_id.id),
                      ('project_id', '!=', False), ('date_end', '=', False)]
            task_created_inspection = self.env['survey.user_input'].sudo().search([('parent_survey_id', '=', rec.survey_id.id)])
            if task_created_inspection:
                domain.append(('id', 'not in', task_created_inspection.mapped('task_id').ids))
            rec.task_id_domain = domain

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.task_id = False

    def create_inspection(self):
        exists_inspection = self.env['survey.user_input'].sudo().search([('survey_id', '=', self.survey_id.id), ('user_id', '=', self.task_id.user_id.id), ('task_id', '=', self.task_id.id)]).exists()
        if exists_inspection:
            raise UserError(_('An inspection has already been assigned to the user of this activity.'))
        inspection_vals = {
            'project_id': self.project_id.id,
            'task_id': self.task_id.id,
            'user_id': self.task_id.user_id.id,
            'survey_id': self.survey_id.copy(self.survey_id.prepare_clone_survey_vals()).id,
            'parent_survey_id': self.survey_id.id,
            'state': 'new',
            'partner_id': self.task_id.user_id.partner_id.id,
            'email': self.task_id.user_id.partner_id.email,
            'test_entry': False,
            'deadline': self.task_id.date_deadline
        }
        self.env['survey.user_input'].create(inspection_vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _('Inspection successfully created.'),
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }
