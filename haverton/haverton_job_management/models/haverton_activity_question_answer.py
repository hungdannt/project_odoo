# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class HavertonActivityQuestionAnswer(models.Model):
    _name = 'haverton.activity.question.answer'
    _description = 'Haverton Activity Question Answer'
    _inherit = 'abstract.uuid'

    haverton_question_uuid = fields.Char()
    haverton_activity_uuid = fields.Char()
    note = fields.Text()
    question_id = fields.Many2one('haverton.service.question')
    is_completed = fields.Boolean(string='Completed')
    is_not_applicable = fields.Boolean(string='N/A')
    task_id = fields.Many2one('project.task')

    _sql_constraints = [
        (
            "task_question_uniq",
            "unique(task_id, question_id)",
            "An answer of this question already exists in this task."
        )
    ]
