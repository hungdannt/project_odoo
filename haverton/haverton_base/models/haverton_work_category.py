# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonWorkCategory(models.Model):
    _name = 'haverton.work.category'
    _description = 'Haverton Work Category'
    _inherit = 'abstract.uuid'
    _rec_name = 'description'

    description = fields.Char(required=True)
