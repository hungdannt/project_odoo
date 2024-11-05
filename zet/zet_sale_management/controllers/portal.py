import json
from odoo.addons.sale.controllers import portal
from odoo import http
from collections import OrderedDict


from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class CustomerPortal(portal.CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/history'], type='http', auth="user", website=True)
    def portal_my_orders_history(self, order_id, access_token=None, **kwargs):
        try:
            order_sudo = self._document_check_access(
                'sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        value = {
            'sale_order': order_sudo,
            'historys': order_sudo.order_history_ids
        }
        return request.render("zet_sale_management.portal_my_orders_history", value)

    @http.route(['/my/orders/history/<int:history>'], type='http', auth="public", website=True)
    def portal_order_history_detail(self, history, report_type=None, access_token=None, message=False, download=False, downpayment=None, **kw):
        try:
            order_history_sudo = self._document_check_access(
                'sale.order.history', history, access_token=access_token)
            order_sudo = order_history_sudo.order_id
        except (AccessError, MissingError):
            return request.redirect('/my')
        access_token = order_sudo._portal_ensure_token()
        return self.portal_order_page(order_sudo.id, report_type, access_token, message, download, downpayment, **kw)

    def _get_page_view_values(self, document, access_token, values, session_history, no_breadcrumbs, **kwargs):
        res = super()._get_page_view_values(document, access_token,
                                            values, session_history, no_breadcrumbs, **kwargs)
        res['data'] = {}
        if request.params.get('history'):
            order_history_sudo = self._document_check_access(
                'sale.order.history', request.params.get('history'), access_token=access_token)
            res['history'] = order_history_sudo
            res['data'] = json.loads(order_history_sudo.old_value)
            res['data']['signature'] = order_history_sudo.signature
        elif hasattr(document, 'get_old_value'):
            res['data'] = json.loads(document.get_old_value())
        return res

    def _prepare_sale_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, filterby=None,  **kwargs
    ):
        value = super()._prepare_sale_portal_rendering_values(
            page, date_begin, date_end, sortby, quotation_page, **kwargs)
        searchbar_filters = self._get_sale_order_searchbar_filters()
        value['searchbar_filters'] = OrderedDict(
            sorted(searchbar_filters.items()))
        value['orders'] = value['orders'] = value['orders'].filtered_domain(
            searchbar_filters.get(filterby, {'domain':[]})['domain'])
        value['filterby'] =  filterby,
        return value

    def _get_sale_order_searchbar_filters(self):
        return {
            'all': {'label': _('All'), 'domain': []},
            'pda': {'label': _('PDA'), 'domain': [('is_fda', '=', False)]},
            'fda': {'label': _('FDA'), 'domain': [('is_fda', '=', True)]},
        }
