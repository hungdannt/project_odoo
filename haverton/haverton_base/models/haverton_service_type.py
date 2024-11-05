# -*- coding: utf-8 -*-
from odoo import fields, models


class HavertonServiceType(models.Model):
    _name = 'haverton.service.type'
    _description = 'Haverton Service Type'
    _inherit = 'abstract.uuid'
    _rec_name = 'description'

    description = fields.Char(required=True)
    system_code = fields.Char()
    work_category_id = fields.Many2one('haverton.work.category')
