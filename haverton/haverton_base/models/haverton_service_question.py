# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonServiceQuestion(models.Model):
    _name = 'haverton.service.question'
    _description = 'Haverton Service Question'
    _inherit = 'abstract.uuid'
    _rec_name = 'question'

    sequence = fields.Integer()
    question = fields.Char()
