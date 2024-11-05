from odoo import fields, models


class SurveyQuestionRuleAction(models.Model):
    _name = 'survey.question.rule.action'
    _description = 'Haverton Inspection Question Rule Action'
    _order = 'type,is_main_action,id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    type = fields.Selection([
        ('visible', 'Visible')
    ])
    opposite_action_id = fields.Many2one('survey.question.rule.action')
    is_main_action = fields.Boolean(
        help='Is the main action in the action type.')

    _sql_constraints = [
        ("code_unique", "unique(code)", "The code must be unique."),
    ]
