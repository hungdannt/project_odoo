# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonDefectCategory(models.Model):
    _name = 'haverton.defect.category'
    _description = 'Haverton Defect Category'
    _inherit = 'abstract.uuid'

    name = fields.Char(required=True)
    category_type = fields.Integer()
    active = fields.Boolean(default=True)
    is_default_new = fields.Boolean()
    is_default_from_activity = fields.Boolean()
