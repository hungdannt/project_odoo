# -*- coding: utf-8 -*-
from odoo import fields, models


class IrUiMenu(models.Model):
    _description = 'Menu'
    _inherit = 'ir.ui.menu'

    mobile_visibility = fields.Boolean(default=False)
    haverton_menu_key = fields.Char(
        help='Used to identify for the menu items.')
