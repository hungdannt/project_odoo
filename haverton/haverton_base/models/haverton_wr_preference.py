# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonWrPreference(models.Model):
    _name = 'haverton.wr.preference'
    _description = 'Haverton Work Release Preference'
    _inherit = 'abstract.uuid'

    name = fields.Char(required=True)
