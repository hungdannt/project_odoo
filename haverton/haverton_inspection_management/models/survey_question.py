# -*- coding: utf-8 -*-
import copy

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .survey_question_rule import OPPOSITE_OPERATOR

HAVERTON_QUESTION_TYPE_MAPPING = {
    'yes_no_question': 'simple_choice',
    'simple_choice': 'simple_choice',
    'multiple_choice': 'multiple_choice',
    'location': 'text_box',
    'signature': 'text_box',
    'multiple_image': 'text_box',
    'multiple_video': 'text_box',
    'date': 'date',
    'datetime': 'datetime',
    'static_text': 'text_box',
    'text_box': 'text_box',
    'char_box': 'char_box',
    'numerical_box': 'numerical_box',
    'acknowledgment': 'text_box',
}

CHOICE_QUESTION_TYPES = ['simple_choice', 'multiple_choice']

QUESTION_TEMPLATE_COPY_FIELDS = ['title', 'question_type', 'haverton_question_type', 'suggested_answer_ids',
                                 'description', 'comments_allowed',
                                 'comment_count_as_answer', 'comments_message', 'triggering_answer_ids',
                                 'constr_mandatory', 'constr_error_msg', 'is_time_limited', 'time_limit',
                                 'allow_no_answer', 'value_static_text', 'autofill_user', 'label_for_user_id',
                                 'autofill_datetime', 'autofill_location', 'view_in_map', 'autofill', 'autofill_field']

DEFAULT_YES_NO_QUESTION_ANSWERS = [
    [0, 0, {'sequence': 1, 'value': 'Yes'}],
    [0, 0, {'sequence': 2, 'value': 'No'}]
]


class SurveyQuestion(models.Model):
    _name = 'survey.question'
    _description = 'Haverton Inspection Question'
    _inherit = ['survey.question', 'abstract.uuid']

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    haverton_question_type = fields.Selection([
        ('yes_no_question', 'Yes/No'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('location', 'Map & Location'),
        ('multiple_image', 'Multiple Images'),
        ('multiple_video', 'Multiple Videos'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('signature', 'Signature'),
        ('static_text', 'Static Text'),
        ('numerical_box', 'Numerical Value'),
        ('char_box', 'Single Line Text Box'),
        ('text_box', 'Multiple Lines Text Box'),
        ('acknowledgment', 'Acknowledgement')], string='Question Type')
    view_in_map = fields.Boolean(default=False)
    is_required = fields.Boolean(default=False)
    allow_no_answer = fields.Boolean(string="Allow N/A", default=False)
    autofill_user = fields.Boolean(
        string="Auto fill user", default=False, help="Used for the Signature question.")
    autofill_datetime = fields.Boolean(
        string="Auto fill Time Stamp", default=False, help="Used for the Signature question.")
    autofill_location = fields.Boolean(
        string="Auto fill Geo Location", default=False, help="Used for the Signature question.")
    label_for_user_id = fields.Char(
        string='Label For User', default='Site Supervisor', help='Label for user answer')
    value_static_text = fields.Text(string="Static Text Value")
    value_acknowledgment = fields.Text(string="Value Acknowledgment")
    text_before_click = fields.Text(help="Text to display before clicking for acknowledgment question")
    text_after_click = fields.Text(help="Text to display after clicking for acknowledgment question")
    
    is_template = fields.Boolean(string="Is Question Template", default=False, copy=False)
    survey_question_template_id = fields.Many2one('survey.question', string="Question template", domain="[('is_template', '=', True)]", copy=False)
    related_question_ids = fields.One2many('survey.question', 'survey_question_template_id', domain="[('is_template', '=', False)]", copy=False)
    is_onchange_template = fields.Boolean(default=False, copy=False)
    original_question_id = fields.Many2one('survey.question', copy=False)
    rule_ids = fields.One2many('survey.question.rule', 'question_id', copy=True)
    autofill = fields.Boolean(string="Auto fill", default=False)
    autofill_field = fields.Selection([('activity_name', 'Activity Name'), ('user_id', 'User'), ('job_address', 'Job Address'), ('contract_no', 'Job Number')])

    @api.constrains('haverton_question_type', 'value_static_text')
    def _check_value_static_text(self):
        for rec in self:
            if rec.haverton_question_type == 'static_text' and not rec.value_static_text:
                raise ValidationError(
                    _('The static text value is required in the static text question')
                )
                
    @api.constrains('haverton_question_type', 'value_acknowledgment', 'text_before_click', 'text_after_click')
    def _check_value_acknowledgment(self):
        for rec in self:
            if rec.haverton_question_type == 'acknowledgment' and not rec.value_acknowledgment:
                raise ValidationError(
                    _('The acknowledgment value is required in the acknowledgment question')
                )
            if rec.haverton_question_type == 'acknowledgment' and not rec.text_before_click:
                raise ValidationError(
                    _('The text before click value is required in the acknowledgment question')
                )
            if rec.haverton_question_type == 'acknowledgment' and not rec.text_after_click:
                raise ValidationError(
                    _('The text after click value is required in the acknowledgment question')
                )

    @api.onchange('haverton_question_type')
    def _onchange_haverton_question_type(self):
        self.autofill = False
        if self.is_onchange_template and self.survey_question_template_id.haverton_question_type == self.haverton_question_type:
            self.is_onchange_template = False
            return
        self.suggested_answer_ids = False
        if self.haverton_question_type:
            self.question_type = HAVERTON_QUESTION_TYPE_MAPPING.get(
                self.haverton_question_type)
            if self.question_type != 'location':
                self.view_in_map = False
            if self.question_type != 'signature':
                self.autofill_user = False
                self.autofill_datetime = False
                self.autofill_location = False
            if self.haverton_question_type == 'yes_no_question':
                self.suggested_answer_ids = copy.deepcopy(
                    DEFAULT_YES_NO_QUESTION_ANSWERS)

    @api.onchange('haverton_question_type', 'allow_no_answer')
    def _onchange_allow_no_answer(self):
        if self.haverton_question_type != 'yes_no_question':
            return
        self.suggested_answer_ids = False
        new_suggested_answer_ids = copy.deepcopy(
            DEFAULT_YES_NO_QUESTION_ANSWERS)
        if self.allow_no_answer:
            new_suggested_answer_ids.append(
                [0, 0, {'sequence': 3, 'value': 'N/A'}])
        self.suggested_answer_ids = new_suggested_answer_ids

    @api.onchange('survey_question_template_id')
    def _onchange_survey_question_template_id(self):
        self.is_onchange_template = True
        if not self.survey_question_template_id:
            return
        updated_fields = QUESTION_TEMPLATE_COPY_FIELDS
        old_values = self.env.context.get('old_values', [])
        if old_values:
            updated_fields = list({key for value in old_values.values() for key in value.keys() if key in QUESTION_TEMPLATE_COPY_FIELDS})
        template_question = self.survey_question_template_id
        update_vals = {field: getattr(template_question, field) for field in updated_fields if field != 'suggested_answer_ids'}
        self.write(update_vals)
        if 'suggested_answer_ids' in updated_fields:
            self.suggested_answer_ids = False
            self.suggested_answer_ids = [
                [0, 0, {'value': answer.value, 'sequence': answer.sequence, 'is_correct': answer.is_correct}] for answer
                in getattr(template_question, 'suggested_answer_ids')]

    def update_related_survey_question(self):
        for rec in self:
            for related_question in rec.related_question_ids:
                related_question._onchange_survey_question_template_id()

    def get_trigger_question_inspection_rule(self, trigger_question, rule, is_otherwise_action=False):
        """
        Return the inspection rule info: conditions for action/otherwise_action to trigger_question
        """
        action = rule.otherwise_action if is_otherwise_action else rule.action
        # get operator to compare the answer with values
        # if the action is not show or the otherwise_action is show, will use the opposite operator
        operator = rule.operator
        if (not is_otherwise_action and not action.is_main_action) or (is_otherwise_action and action.is_main_action):
            operator = OPPOSITE_OPERATOR[rule.operator]
        return {
            'trigger_question_uuid': trigger_question.uuid,
            'condition': {
                # action is used to filter by action and check is_main_action
                'action': action,
                # question_sequence is used to choose the last question (same as FastField)
                'question_sequence': self.sequence,
                # rule_sequence is used to choose the first rule (same as FastField)
                'rule_sequence': rule.sequence,
                # rule_id is used to choose the first rule (same as FastField)
                'rule_id': rule.id,
                'question_uuid': self.uuid,
                'values': rule.choice_answer_ids.mapped('uuid') if self.question_type in CHOICE_QUESTION_TYPES else eval(rule.values),
                'operator': operator,
            },
        }

    def extract_rule(self, rule):
        self.ensure_one()
        trigger_question_inspection_rules = []
        for question in rule.trigger_question_ids:
            trigger_question_inspection_rules.append(
                self.get_trigger_question_inspection_rule(question, rule))
            if rule.otherwise_action:
                trigger_question_inspection_rules.append(
                    self.get_trigger_question_inspection_rule(question, rule, is_otherwise_action=True))
        return trigger_question_inspection_rules

    def get_inspection_rules(self):
        results = []
        for rec in self:
            for rule in rec.rule_ids:
                results.extend(rec.extract_rule(rule))
        return results

    def prepare_copy_data(self, data_list):
        for data in data_list:
            data['original_question_id'] = self.id
        return data_list

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        data_list = super().copy_data(default)
        data_list = self.prepare_copy_data(data_list)
        return data_list

    def create_question_template(self, default=None):
        self.ensure_one()
        val_update = {
            'is_template': True,
            'is_page': False,
            'survey_id': None,
            'is_onchange_template': False,
            'original_question_id': None
        }
        if default:
            val_update.update(default)
        super().copy(val_update)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success!',
                'type': 'success',
                'message': 'Created question template successfully.',
                'sticky': False,
            }
        }
