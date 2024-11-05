# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonLocation(models.Model):
    _name = 'haverton.location'
    _description = 'Haverton Location'
    _inherit = 'abstract.uuid'
    _order = 'sequence'

    name = fields.Char(required=True)
    sequence = fields.Integer()
    haverton_active = fields.Boolean(default=True)
