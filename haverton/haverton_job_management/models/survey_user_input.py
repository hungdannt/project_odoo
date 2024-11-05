# -*- coding: utf-8 -*-

from odoo import models


class SurveyUserInput(models.Model):
    _name = 'survey.user_input'
    _description = 'Haverton Inspection'
    _inherit = ['survey.user_input', 'abstract.uuid']
