# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SurveyUserInputLine(models.Model):
    _name = 'survey.user_input.line'
    _inherit = ['abstract.survey.user.signature', 'survey.user_input.line', 'abstract.uuid']

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    attach_map_image = fields.Many2one('ir.attachment', string='Map Image')
    location = fields.Json()
    user_id = fields.Many2one('res.users')
    is_clicked = fields.Boolean(default=False, help="Is acknowledgment button clicked")

    @api.constrains('skipped', 'answer_type')
    def _check_answer_type_skipped(self):
        return True
