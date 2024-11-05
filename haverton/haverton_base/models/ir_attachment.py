# -*- coding: utf-8 -*-
from odoo import models


class IrAttachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'abstract.uuid']

