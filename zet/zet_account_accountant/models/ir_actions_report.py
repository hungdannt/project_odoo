# -*- coding: utf-8 -*-

from odoo import models



class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'


    def _get_rendering_context(self, report, docids, data):
        data = super()._get_rendering_context(report, docids, data)
        data['proforma'] = False
        return data
