import calendar
from odoo import models, fields
from datetime import timedelta


class IrSequence(models.Model):
    _inherit = 'ir.sequence'


    def _create_date_range_seq(self, date):
        if self.code != 'sale.order':
            return super()._create_date_range_seq(date)
        obj_date_range = self.env['ir.sequence.date_range']
        year = fields.Date.from_string(date).year
        month = fields.Date.from_string(date).month

        date_from = '{}-{}-01'.format(year, month)
        date_end = calendar.monthrange(year, month)[1]
        date_to = '{}-{}-{}'.format(year, month, date_end)
        date_range = obj_date_range.search([('sequence_id', '=', self.id), ('date_from', '>=', date), ('date_from', '<=', date_to)], order='date_from desc', limit=1)
        if date_range:
            date_to = date_range.date_from + timedelta(days=-1)
        date_range = obj_date_range.search([('sequence_id', '=', self.id), ('date_to', '>=', date_from), ('date_to', '<=', date)], order='date_to desc', limit=1)
        if date_range:
            date_from = date_range.date_to + timedelta(days=1)
        seq_date_range = obj_date_range.sudo().create({
            'date_from': date_from,
            'date_to': date_to,
            'sequence_id': self.id,
        })
        return seq_date_range
