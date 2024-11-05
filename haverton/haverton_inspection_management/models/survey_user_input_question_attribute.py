# -*- coding: utf-8 -*-
from odoo import fields, models


class SurveyUserInputQuestionAttribute(models.Model):
    _name = 'survey.user_input.question.attribute'
    _description = 'Question Attribute In Inspection'

    user_input_id = fields.Many2one(
        'survey.user_input', required=True, ondelete='cascade')
    question_id = fields.Many2one(
        'survey.question', required=True, ondelete='cascade')
    visible = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "unique_relation",
            "unique(question_id, user_input_id)",
            "This question was existed in this user input.",
        )
    ]

    def get_user_input_question_attribute(self, user_input, question):
        return self.search([('user_input_id.id', '=', user_input.id), ('question_id.id', '=', question.id)], limit=1)
