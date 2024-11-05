# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonCompliance(models.Model):
    _name = 'haverton.compliance'
    _description = 'Haverton Compliance'
    _inherit = 'abstract.uuid'

    name = fields.Char(required=True)
    font_color = fields.Char(size=32)
    bgr_color = fields.Char(string='Background Color', size=32)
