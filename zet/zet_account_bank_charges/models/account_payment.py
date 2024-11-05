from odoo import  models, fields, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    move_bankcharge_ids = fields.One2many('account.move', 'bankcharge_id')
    
    def _get_value_create_invoice_from_back_charges(self, bank_charges_line_name):
        value = super()._get_value_create_invoice_from_back_charges(bank_charges_line_name)
        currency = self.journal_id.currency_id or self.env.company.currency_id
        if self.currency_id != currency:
            line_ids = value.get('line_ids')
            for line in line_ids:
                if len(line) >=3:
                    line[2]['amount_currency'] = self.bank_charges if line[2].get('debit') > 0 else -self.bank_charges
                    line[2]['currency_id'] = self.currency_id.id
                    line[2]['debit'] = self.currency_id._convert(from_amount=line[2].get('debit'), to_currency=self.company_id.currency_id,company=self.company_id, date=self.date)
                    line[2]['credit'] = self.currency_id._convert(from_amount=line[2].get('credit'), to_currency=self.company_id.currency_id,company=self.company_id, date=self.date)
        value['bankcharge_id'] = self.id
        return value

    def button_open_bank_charge(self):
        self.ensure_one()
        if len(self.move_bankcharge_ids) == 1:
            return self._get_records_action_views(self.move_bankcharge_ids.name, self.move_bankcharge_ids.id)
        elif len(self.move_bankcharge_ids) > 1:
            name = _('Bank Charges')
            return self._get_records_action_views(name=name, view_mode='tree,form', domain=[('id', 'in', self.move_bankcharge_ids.ids)])

    def _get_records_action_views(self, name, res_id=0, view_mode='form', domain=[]):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'view_mode': view_mode,
            'res_model': 'account.move',
            'res_id': res_id,
            'domain': domain
        }
