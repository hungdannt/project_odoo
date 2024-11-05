from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    inspection_ids = fields.One2many('survey.user_input', 'task_id')
    inspection_status = fields.Char(compute="_compute_inspection_status")

    @api.depends('inspection_ids')
    def _compute_inspection_status(self):
        for rec in self:
            if not rec.inspection_ids:
                rec.inspection_status = False
            else:
                states = set(rec.inspection_ids.mapped('state'))
                rec.inspection_status = next(iter(states)) if len(states) == 1 else 'in_progress'

    def generate_inspections_from_activity_service_questions(self):
        domain = self.get_alive_activity_due_next_week_domain()
        for task in self.search(domain):
            for service_question_answer in task.haverton_activity_question_answer_ids:
                question_id = service_question_answer.question_id
                if not question_id or not question_id.is_inspection_question:
                    continue
                survey = question_id._get_survey()
                if not survey:
                    continue
                user_input_model = self.env['survey.user_input']
                existed_inspection = user_input_model.check_inspection_existed(
                    survey, task)
                if existed_inspection:
                    continue
                inspection_vals = user_input_model.prepare_inspection_creation_vals(
                    survey, task.project_id, task)
                user_input_model.create(inspection_vals)
