from odoo import api, fields, models
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    calendar = fields.Date(string='Payment Terms')
    is_required_user = fields.Boolean(string="Check user", compute="_compute_show_dob_field")
    date_order = fields.Datetime(string='Order Date', required=True, readonly=False, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    custom_create_date = fields.Datetime(string='Creation Date', compute='_compute_date_new', store=True, readonly=False, index=True, help="Date on which sales order is created.")

    @api.depends('user_id')
    def _compute_show_dob_field(self):
        for order in self:
            order.is_required_user = order.user_id.login == "lumber2051@yahoo.co.jp"

    @api.onchange('calendar')
    def _onchange_partner_id(self):
        self.payment_term_id = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if self.user_id.login == "lumber2051@yahoo.co.jp":
            self.payment_term_id = False

    @api.depends('create_date')
    def _compute_date_new(self):
        for rec in self:
            rec.custom_create_date = rec.create_date.date()





