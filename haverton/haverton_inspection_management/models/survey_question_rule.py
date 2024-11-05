from odoo import api, fields, models

SURVEY_QUESTION_RULE_OPERATOR = {
    'equals': 'Equals',
    'not_equals': 'Does not equal',
}

OPPOSITE_OPERATOR = {
    'equals': 'not_equals',
    'not_equals': 'equals',
}


class SurveyQuestionRule(models.Model):
    _name = 'survey.question.rule'
    _description = 'Haverton Inspection Question Rule'
    _order = 'sequence,id'

    sequence = fields.Integer('Sequence', default=10)
    original_rule_id = fields.Many2one('survey.question.rule', copy=False)
    question_id = fields.Many2one(
        'survey.question', required=True, ondelete='cascade')
    survey_id = fields.Many2one(related='question_id.survey_id')
    operator = fields.Selection(
        [*SURVEY_QUESTION_RULE_OPERATOR.items()], required=True)
    values = fields.Text(
        default=[], help='List of values to check with the operator.')
    choice_answer_ids = fields.Many2many(
        comodel_name='survey.question.answer',
        relation='survey_question_rule_answer_rel',
        column1='rule_id',
        column2='answer_id',
        copy=False,
    )
    action = fields.Many2one('survey.question.rule.action', required=True)
    otherwise_action = fields.Many2one('survey.question.rule.action')
    trigger_question_ids = fields.Many2many(
        string='Target Questions',
        comodel_name='survey.question',
        relation='survey_question_rule_rel',
        column1='rule_id',
        column2='trigger_question_id',
        copy=False,
    )

    def get_survey_clone_rule(self, survey):
        self.ensure_one()
        return self.search([('original_rule_id', '=', self.id), ('survey_id', '=', survey.id)], limit=1)

    def get_rule_clone_trigger_questions(self, survey):
        self.ensure_one()
        return self.env['survey.question'].search([('original_question_id', 'in', self.trigger_question_ids.ids), ('survey_id', '=', survey.id)])

    def get_rule_clone_choice_answers(self, survey):
        self.ensure_one()
        return self.env['survey.question.answer'].search([('original_answer_id', 'in', self.choice_answer_ids.ids), ('question_id.survey_id', '=', survey.id)])

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        data_list = super().copy_data(default)
        for data in data_list:
            data['original_rule_id'] = self.id
        return data_list
