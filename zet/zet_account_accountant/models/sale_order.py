from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped, final, date)
        for move in moves:
            order_id = move.line_ids.sale_line_ids.order_id[0]
            move.write({
                'vessel_name': order_id.vessel_name,
                'port': order_id.port,
                'date_of_arrival': order_id.date_of_arrival,
                'date_of_departure': order_id.date_of_departure,
                'foreign_currency_id': order_id.foreign_currency_id
            })
        return moves
