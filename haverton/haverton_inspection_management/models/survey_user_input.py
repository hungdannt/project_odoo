# -*- coding: utf-8 -*-

import base64
import logging
import re

from odoo import Command, _, api, fields, models
from odoo.addons.haverton_base.tools.datetime import (
    convert_datetime_to_user_lang_format,
)
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__file__)


class SurveyUserInput(models.Model):
    _name = 'survey.user_input'
    _inherit = ['abstract.survey.user.signature', 'survey.user_input']

    name = fields.Char(related='survey_id.title', store=True)
    project_id = fields.Many2one('project.project', string="Job")
    task_id = fields.Many2one('project.task', string="Activity")
    activity_name = fields.Char(related='task_id.name', store=True)
    address = fields.Text(related='task_id.project_id.address_details', store=True)
    job_address = fields.Char(related='project_id.address')
    deadline = fields.Datetime('Due Date')
    overdue = fields.Boolean(compute='_compute_overdue', store=True)
    user_id = fields.Many2one('res.users', 'Site Supervisor')
    aggregate_location_image = fields.Many2one('ir.attachment', string='Aggregate Location Image')
    sign_datetime = fields.Datetime()
    sequence = fields.Integer()
    house_design = fields.Char()
    defect_ids = fields.One2many('project.task', 'inspection_id', string="Defects",
                                 domain="[('haverton_task_type', '=', 'defect')]")
    inspection_report_name = fields.Char(compute='_compute_inspection_report_name')
    submit_datetime = fields.Datetime()
    contract_no = fields.Char(related='project_id.contract_no')
    parent_survey_id = fields.Many2one('survey.survey', string="Parent Survey")

    @api.depends('deadline')
    def _compute_overdue(self):
        current_date = fields.Date.today()
        for rec in self:
            rec.overdue = rec.deadline and rec.deadline.date() < current_date

    def check_question_visible(self, question):
        input_question_attribute = self.env['survey.user_input.question.attribute'].get_user_input_question_attribute(
            user_input=self, question=question)
        return input_question_attribute.visible if input_question_attribute else True

    def create_question_dict(self, question):
        return {
            'uuid': question.uuid,
            'title': question.title,
            'haverton_question_type': question.haverton_question_type,
            'view_in_map': question.view_in_map,
            'autofill_user': question.autofill_user,
            'label_for_user_id': question.label_for_user_id,
            'autofill_datetime': question.autofill_datetime,
            'autofill_location': question.autofill_location,
            'constr_mandatory': question.constr_mandatory,
            'autofill': question.autofill,
            'autofill_field': question.autofill_field,
            'suggested_answer_ids': question.suggested_answer_ids.read() or False,
            'answers': self.get_haverton_answer_data(question) or False,
            'visible': self.check_question_visible(question),
            'constr_error_msg': question.constr_error_msg if question.constr_error_msg else False,
            'text_before_click': question.text_before_click if question.text_before_click else False,
            'text_after_click': question.text_after_click if question.text_after_click else False,
        }

    def prepare_haverton_data(self):
        self.ensure_one()
        response = dict()
        response['sections'] = list()
        non_section_question = self.survey_id.question_ids.filtered(lambda x: not x.page_id)
        if non_section_question:
            response['sections'].append({
                'uuid': " ",
                'title': " ",
                'questions': [self.create_question_dict(q) for q in non_section_question] or False
            })
        for page in self.survey_id.page_ids:
            response['sections'].append({
                'uuid': page.uuid,
                'title': page.title,
                'questions': [self.create_question_dict(q) for q in page.question_ids] or False
            })
        for section in response['sections']:
            self.assign_question_inspection_rules(section)
        inspection_data = self.read()[0]
        if inspection_data.get('user_id'):
            inspection_data['user_id'] = {
                'uuid': self.user_id.uuid,
                'name': self.user_id.name
            }
        if inspection_data.get('project_id'):
            inspection_data['project_id'] = {
                'uuid': self.project_id.uuid,
                'contract_no': self.project_id.contract_no
            }
        if inspection_data.get('aggregate_location_image'):
            inspection_data['aggregate_location_image'] = {
                'uuid': self.aggregate_location_image.uuid,
                'datas': self.aggregate_location_image.datas
            }
        inspection_data['defect_ids'] = self.defect_ids.read() or False
        return {**inspection_data, **response}
    
    def get_question_action_type_conditions(self, question, type: str):
        """
        Returns conditions to do the main action in an action type of question.
        Mobile will check if any true condition in the return values, it will do the main action.
        Params:
        - question: the question data needs to check
        - type: the type data needs to check
        """
        question_inspection_rules = self.survey_id.question_ids.get_inspection_rules()
        action_type_conditions = []
        for question_rule in question_inspection_rules:
            trigger_question_uuid = question_rule.get(
                'trigger_question_uuid', None)
            if trigger_question_uuid is None or (trigger_question_uuid != question.get('uuid', None)):
                continue
            # Check and add the conditions of action here
            condition = question_rule.get('condition')
            if not condition:
                continue
            action = condition.get('action', None)
            if action and action.type == type:
                action_type_conditions.append(condition)
        if action_type_conditions:
            # get the conditions of the first rule in the last question in a survey. (same as FastField)
            last_action_type_condition = sorted(action_type_conditions, key=lambda item: (
                item['question_sequence'], -item['rule_sequence'], -item['rule_id']))[-1]
            # get the action condition and the otherwise condition in the rule contains last_action_type_condition
            last_rule_action_type_conditions = [item for item in action_type_conditions if item.get(
                'rule_id') == last_action_type_condition.get('rule_id')]
            condition_actions = list(set([item['action'] for item in last_rule_action_type_conditions]))
            if len(last_rule_action_type_conditions) > 1 and len(condition_actions) == 1 and not condition_actions[0].is_main_action:
                # both action and otherwise_action in the last rule are not the main action. Ex: always hide
                return []
            return last_rule_action_type_conditions
        return None

    def assign_question_inspection_rules(self, section):
        questions = section.get('questions')
        if not questions:
            return section
        for question in questions:
            inspection_rules = {}
            visible_conditions = self.get_question_action_type_conditions(question=question, type='visible')
            if visible_conditions is not None:
                inspection_rules['visible_conditions'] = visible_conditions
            question['inspection_rules'] = inspection_rules or False
        return section

    def extract_attachment_urls(self, attachments):
        if not attachments:
            return []
        attachment_dicts = attachments.read(['uuid', 'name', 'local_url'])
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url') or ''
        for item in attachment_dicts:
            item.update({
                'local_url': (base_url + item['local_url']) if 'local_url' in item else None
            })
        return attachment_dicts

    def get_haverton_answer_data(self, question):
        self.ensure_one()
        user_input = self.user_input_line_ids.filtered_domain([('question_id', '=', question.id)])
        if not user_input and question.haverton_question_type != 'static_text' and question.haverton_question_type != 'acknowledgment':
            return None

        if question.haverton_question_type == 'static_text':
            user_input_data = {
                'value_text_box': question.value_static_text
            }
        elif question.haverton_question_type == 'acknowledgment':
            user_input_data = {
                'value_text_box': question.value_acknowledgment,
                'is_clicked' : user_input[0].is_clicked if user_input else False
            }
        elif question.question_type in ['simple_choice', 'multiple_choice']:
            user_input_data = {
                'selected_options': [
                    {
                        'uuid': choice.uuid,
                        'value': choice.value
                    }
                    for choice in user_input.mapped('suggested_answer_id')
                ] or False
            }
        else:
            user_input_data = {
                'value_text_box': user_input[0].value_text_box,
                'value_char_box': user_input[0].value_char_box,
                'value_numerical_box': user_input[0].value_numerical_box,
                'location': user_input[0].location,
                'attachment_ids': self.extract_attachment_urls(user_input[0].attachment_ids),
                'value_date': user_input[0].value_date,
                'value_datetime': user_input[0].value_datetime,
                'attach_map_image': user_input[0].attach_map_image,
                'user_signature': user_input[0].user_signature,
                'user_signature_raw': user_input[0].user_signature_raw,
                'user_id': user_input[0].user_id.read(['uuid', 'name'])[0] if user_input[0].user_id else False,
            }
        return user_input_data

    def update_inspection_answer(self, questions_data):
        for data in questions_data:
            question = self.env['survey.question'].sudo().validate_by_uuid(data.uuid)
            answer = self._prepare_answer_value(question.haverton_question_type, data.answers)
            if question.haverton_question_type in ['yes_no_question', 'simple_choice', 'multiple_choice', 'date', 'datetime', 'text_box', 'char_box', 'numerical_box']:
                self._save_lines(question, answer, overwrite_existing=True)
            elif question.haverton_question_type in ['location', 'multiple_image', 'multiple_video', 'signature', 'acknowledgment']:
                self._save_custom_question_type_lines(question, data.answers)

            if data.visible is not None:
                input_question_attribute_model = self.env['survey.user_input.question.attribute']
                input_question_attribute = input_question_attribute_model.get_user_input_question_attribute(
                    user_input=self, question=question)
                if input_question_attribute:
                    input_question_attribute.write({
                        'visible': data.visible
                    })
                else:
                    input_question_attribute = input_question_attribute_model.create({
                        'user_input_id': self.id,
                        'question_id': question.id,
                        'visible': data.visible,
                    })

    def _prepare_answer_value(self, question_type, answer_data):
        if not answer_data or not question_type:
            return False
        if question_type in ['yes_no_question', 'simple_choice', 'multiple_choice'] and answer_data.selected_options:
            choices = self.env['survey.question.answer'].sudo().search([('uuid', 'in', answer_data.selected_options)]).ids
            return choices or False
        elif question_type == 'date' and answer_data.value_date:
            return answer_data.value_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        elif question_type == 'datetime' and answer_data.value_datetime:
            return answer_data.value_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        elif question_type == 'text_box' and answer_data.value_text_box:
            return answer_data.value_text_box
        elif question_type == 'char_box' and answer_data.value_char_box:
            return answer_data.value_char_box
        elif question_type == 'numerical_box' and answer_data.value_numerical_box:
            return answer_data.value_numerical_box
        return False

    def prepare_signature_question_answer(self, vals, answer_data):
        if answer_data.user_signature:
            vals['user_signature'] = answer_data.user_signature
        if answer_data.user_signature_raw:
            vals['user_signature_raw'] = answer_data.user_signature_raw
        if answer_data.user_uuid:
            user_uuid = answer_data.user_uuid
            user = self.env['res.users'].browse_by_uuid(user_uuid)
            if user:
                vals['user_id'] = user.id
        if answer_data.value_datetime:
            vals['value_datetime'] = answer_data.value_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if answer_data.location:
            vals['location'] = answer_data.location
        return vals

    def _save_custom_question_type_lines(self, question, answer_data):
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': question.question_type,
        }
        if question.haverton_question_type == 'location':
            vals['location'] = answer_data.location if answer_data else False
            vals['attach_map_image'] = False
            if answer_data and answer_data.attach_map_image:
                attachment = self.env['ir.attachment'].sudo().search([('uuid', '=', answer_data.attach_map_image)], limit=1)
                if attachment:
                    vals['attach_map_image'] = attachment.id

        elif question.haverton_question_type in ['multiple_image', 'multiple_video'] and answer_data and answer_data.attachment_uuids:
            attachments = self.env['ir.attachment'].sudo().search([('uuid', 'in', answer_data.attachment_uuids)])
            if attachments:
                vals['attachment_ids'] = [Command.set(attachments.ids)]
        elif question.haverton_question_type == 'signature' and answer_data and answer_data.user_signature:
            self.prepare_signature_question_answer(vals, answer_data)
        elif question.haverton_question_type == 'acknowledgment' and answer_data and answer_data.is_clicked:
            vals['is_clicked'] = answer_data.is_clicked
        if old_answers:
            old_answers.sudo().write(vals)
            return old_answers
        else:
            return self.env['survey.user_input.line'].sudo().create(vals)

    @api.depends('survey_id', 'user_id', 'sign_datetime')
    def _compute_inspection_report_name(self):
        for rec in self:
            sign_date = rec.sign_datetime.strftime('%d-%m-%Y') if rec.sign_datetime else None
            rec.inspection_report_name = ' '.join(
                filter(None, (
                    rec.survey_id.title,
                    sign_date,
                    rec.user_id.name
                ))
            ) or 'Inspection Report'

    def convert_datetime_format(self, date):
        return convert_datetime_to_user_lang_format(date)
    
    def get_base64_user_signature(self):
        return base64.b64encode(self.user_signature.encode()).decode()
    
    def get_style_user_signature(self):
        viewbox_pattern = re.compile(r'viewBox="([^"]*)"')
        match = viewbox_pattern.search(self.user_signature)
        if not match:
            return "width: 224px; height: 167px;"
        viewbox_value = match.group(1)
        viewbox_components = viewbox_value.split()
        try:
            width = int(viewbox_components[2])
            height = int(viewbox_components[3])
            return f"width: {width}px; height: {height}px;"
        except:
            return "width: 224px; height: 167px;"

    def prepare_inspection_creation_vals(self, survey, project, task):
        user = task.user_id if task else self.env.user
        return {
            'project_id': project.id,
            'task_id': task.id,
            'user_id': user.id,
            'survey_id': survey.copy({'is_clone': True, 'title': survey.title}).id,
            'parent_survey_id': survey.id,
            'state': 'new',
            'partner_id': user.partner_id.id,
            'email': user.partner_id.email,
            'test_entry': False,
            'deadline': task.date_deadline
        }

    def get_inspection(self, survey, task):
        if not survey or not task:
            return
        return self.env['survey.user_input'].sudo().search(
            [('parent_survey_id', '=', survey.id), ('user_id', '=', task.user_id.id), ('task_id', '=', task.id)])

    def check_inspection_existed(self, survey, task):
        inspection = self.get_inspection(survey, task)
        return True if inspection else False

    def action_after_submitted(self):
        self.ensure_one()
        inspection_submitted_template = self.env.ref(
            'haverton_inspection_management.mail_template_after_submit_inspection', raise_if_not_found=False)
        if inspection_submitted_template:
            try:
                inspection_submitted_template.send_mail(self.id)
            except Exception as e:
                _logger.warning(str(e))

    def write(self, vals):
        res = super().write(vals)
        if vals.get('state') == 'done':
            for rec in self:
                rec.action_after_submitted()
        return res
