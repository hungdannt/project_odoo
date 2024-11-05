# -*- coding: utf-8 -*-

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, so_lines):
        value = super()._prepare_invoice_values(order, so_lines)
        value.update({
            'vessel_name': order.vessel_name,
            'port': order.port,
            'date_of_arrival': order.date_of_arrival,
            'date_of_departure': order.date_of_departure,
            'foreign_currency_id': order.foreign_currency_id.id
        })
        return value
