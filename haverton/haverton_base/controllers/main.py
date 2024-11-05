import re

from odoo import http, tools
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request
from werkzeug.utils import redirect


class HavertonAuthSignupHome(AuthSignupHome):
    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        """
        Overwrite the base function to reset_password.
        - If mobile: Open app or redirect to store.
        - If desktop: Open web and follow the base flow.
        """
        user_agent = request.httprequest.headers.environ.get('HTTP_USER_AGENT')
        is_ios_device = bool(
            re.search(r'iPhone|Mac OS', user_agent, re.IGNORECASE))
        is_android_device = bool(
            re.search(r'Android', user_agent, re.IGNORECASE))
        if not is_ios_device and not is_android_device:
            # desktop
            return super().web_auth_reset_password(*args, **kw)
        schema_link = request.env['ir.config_parameter'].sudo().get_param(
            'haverton_base.mobile_schema_link'
        )
        if schema_link:
            return redirect(schema_link + 'token=' + kw.get('token', ''))
        if is_ios_device:
            appstore_url = request.env['ir.config_parameter'].sudo().get_param(
                'haverton_base.appstore_url'
            ) or 'https://www.apple.com/app-store/'
            return redirect(appstore_url)
        else:
            google_play_url = request.env['ir.config_parameter'].sudo().get_param(
                'haverton_base.google_play_url'
            ) or 'https://play.google.com/'
            return redirect(google_play_url)
