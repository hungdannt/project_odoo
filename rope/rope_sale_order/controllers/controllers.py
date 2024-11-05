# -*- coding: utf-8 -*-
# from odoo import http


# class RopeSaleOrder(http.Controller):
#     @http.route('/rope_sale_order/rope_sale_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rope_sale_order/rope_sale_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rope_sale_order.listing', {
#             'root': '/rope_sale_order/rope_sale_order',
#             'objects': http.request.env['rope_sale_order.rope_sale_order'].search([]),
#         })

#     @http.route('/rope_sale_order/rope_sale_order/objects/<model("rope_sale_order.rope_sale_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rope_sale_order.object', {
#             'object': obj
#         })
