# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class HavertonActivityQuestionAnswer(models.Model):
    _inherit = 'haverton.activity.question.answer'
    _description = 'Haverton Activity Question Answer'

    is_completed = fields.Boolean(
        string='Completed', compute='_compute_is_completed', store=True, readonly=False)

    @api.depends('question_id', 'task_id', 'task_id.inspection_ids.submit_datetime', 'task_id.inspection_ids.state')
    def _compute_is_completed(self):
        for rec in self:
            is_completed = rec.is_completed
            if not is_completed:
                if rec.question_id and rec.question_id.is_inspection_question and rec.task_id:
                    try:
                        survey = rec.question_id.get_survey()
                        inspections = self.env['survey.user_input'].sudo().search(
                            [('parent_survey_id', '=', survey.id), ('task_id', '=', rec.task_id.id), ('user_id', '=', rec.task_id.user_id.id)])
                        if not inspections.exists():
                            is_completed = False
                        else:
                            existed_incompleted_inspection = inspections.filtered_domain(
                                [('submit_datetime', '=', False)]).exists()
                            is_completed = False if existed_incompleted_inspection else True
                    except UserError:
                        pass
            rec.is_completed = is_completed
