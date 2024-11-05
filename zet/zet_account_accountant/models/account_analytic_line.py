from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    customer_id = fields.Many2one('res.partner', string="Customer")
