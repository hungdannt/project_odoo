from odoo import models
from odoo.addons.zet_custom_name_sale_invoice.models.sale_order import PREFIX_PDA, PREFIX_FDA


PREFIX_OUT_INVOICE = 'I'
PREFIX_OUT_REFUND = 'C'

class AccountMove(models.Model):
    _inherit = 'account.move'


    def _get_last_sequence(self, relaxed=False, with_prefix=None):
        if self.move_type == 'out_refund' and self.reversed_entry_id:
            prefix = PREFIX_OUT_REFUND
            name_replace = self.reversed_entry_id.name.replace('I', '')
        elif self.move_type == 'out_invoice' and self.line_ids.sale_line_ids.order_id:
            prefix = PREFIX_OUT_INVOICE
            name_replace = self.line_ids.sale_line_ids.order_id.name.replace(PREFIX_PDA, '').replace(PREFIX_FDA, '')

        if self.move_type in ['out_refund', 'out_invoice'] and (self.reversed_entry_id or self.line_ids.sale_line_ids.order_id):
            query = f"""
                SELECT name
                FROM {self._table}
                WHERE name LIKE %s
                ORDER BY name DESC
                LIMIT 1;
            """
            self.env.cr.execute(query, (f'{prefix}{name_replace}-%',))
            highest_name = self.env.cr.fetchone()
            if highest_name:
                return highest_name[0]
            return f'{prefix}{name_replace}-00'

        return super()._get_last_sequence(relaxed, with_prefix)


    @property
    def _sequence_yearly_regex(self):
        acount_move = self.reversed_entry_id
        if acount_move and self.move_type == 'out_refund':
            return self.journal_id.sequence_override_regex or r'^(?P<prefix1>.*?)(?P<year>(?:19|20|21)\d{2})/(?P<month>\d{2})(?P<suffix>.*)$'
        return super()._sequence_yearly_regex