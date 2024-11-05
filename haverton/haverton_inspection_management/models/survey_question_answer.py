# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class SurveyQuestionAnswer(models.Model):
    _name = 'survey.question.answer'
    _description = 'Haverton Inspection Question Answer'
    _inherit = ['survey.question.answer', 'abstract.uuid']

    original_answer_id = fields.Many2one('survey.question.answer', copy=False)

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        data_list = super().copy_data(default)
        for data in data_list:
            data['original_answer_id'] = self.id
        return data_list
