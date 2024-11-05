from odoo import http, tools


class Deeplink(http.Controller):
    @http.route('/.well-known/<string:file_name>', type='http', auth="public", sitemap=False)
    def get_deeplink(self, file_name, **kwargs):
        text_file_path = tools.misc.file_path(
            'haverton_base/static/src/deeplink/%s' % file_name)
        f = open(text_file_path, 'r')
        return http.Response(f.read(), headers={'Content-Type': 'application/json'})
