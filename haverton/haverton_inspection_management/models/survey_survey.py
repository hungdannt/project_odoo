# -*- coding: utf-8 -*-

from odoo import Command, _, api, fields, models

from .survey_question import CHOICE_QUESTION_TYPES


class Survey(models.Model):
    _name = 'survey.survey'
    _description = 'Haverton Inspection Template'
    _inherit = ['survey.survey', 'abstract.uuid']

    project_id = fields.Many2one('project.project', string="Job")
    task_id = fields.Many2one('project.task', string="Activity/Defect")
    is_clone = fields.Boolean(
        string="Is Question Template", default=False, copy=False)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('published', 'Published'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )

    def create_inspection(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Inspection'),
            'res_model': 'inspection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_survey_id': self.id},
            'views': [[False, 'form']]
        }

    def prepare_clone_survey_vals(self):
        return {
            'is_clone': True,
            'title': self.title,
            'state': self.state,
        }

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_publish(self):
        self.write({'state': 'published'})

    def get_survey_by_title(self, title: str):
        if not title:
            return
        return self.search([('title', '=', title.strip()), ('is_clone', '=', False)], limit=1)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        clone = super().copy(default)
        for question in self.question_ids:
            if not question.rule_ids:
                continue
            for rule in question.rule_ids:
                clone_rule = rule.get_survey_clone_rule(clone)
                # assign the copied trigger questions for the copied rule
                clone_rule.trigger_question_ids = [Command.set(
                    rule.get_rule_clone_trigger_questions(clone).ids)]

                # assign the copied choice answers for the copied rule
                if question.question_type not in CHOICE_QUESTION_TYPES:
                    continue
                clone_rule.choice_answer_ids = [Command.set(
                    rule.get_rule_clone_choice_answers(clone).ids)]
        return clone
