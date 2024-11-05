import json
from odoo import api, models, fields, _
from odoo.exceptions import UserError

PREFIX_PDA = "P"
PREFIX_FDA = "F"

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New") and vals.get('is_fda'):
                vals['name'] = self._get_name_fda(vals.get('date_order'))
        return super().create(vals_list)

    def _get_name_fda(self, date_order):
        seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(date_order)
                ) if date_order else None
        return  self.env['ir.sequence'].next_by_code(
                    'sale.order', sequence_date=seq_date).replace(PREFIX_PDA, PREFIX_FDA) or _("New")

 
    def update_value_create_fda(self):
        value = super().update_value_create_fda()
        value['name'] = self.name.replace(PREFIX_PDA, PREFIX_FDA)
        return value
    
    def create_fda(self):
        if len(self.fda.filtered(lambda x:x.state != 'cancel')):
            raise UserError(_('An FDA already exists that refers to this PDA. You cannot create more than one FDA for a single PDA. If you wish to proceed, please cancel the existing FDA first.'))
        return super().create_fda()
    
    def action_draft(self):
        if self.is_fda and self.pda.fda.filtered(lambda x:x.state != 'cancel'):
            raise UserError(_('An FDA already exists that refers to this PDA. You cannot create more than one FDA for a single PDA. If you wish to proceed, please cancel the existing FDA first.'))
        return super().action_draft()
