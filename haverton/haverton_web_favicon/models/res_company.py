import base64
import hashlib
import io
from random import randrange
from PIL import Image
import odoo
from odoo import api, fields, models, tools
from odoo.http import request


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_default_favicon(self):
        img_path = odoo.tools.misc.file_path("haverton_web_favicon/static/img/favicon.ico")
        with tools.file_open(img_path, "rb") as f:
            return base64.b64encode(f.read())
            
    favicon = fields.Binary(
        string="Company Favicon",
        help="This field holds the image used to display favicon for a given company.",
        default=_get_default_favicon
    )

    browser_title = fields.Char(
        help="This field to set the company application title", string="Company Application Title")

    # Get favicon from current company
    @api.model
    def _get_favicon(self):
        """Returns a local url that points to the image field of a given record."""
        company_id = (
            request.httprequest.cookies.get("cids")
            if request.httprequest.cookies.get("cids")
            else False
        )
        company = (
            self.browse(int(company_id.split(",")[0])).sudo()
            if company_id and self.browse(int(company_id.split(",")[0])).sudo().favicon
            else False
        )
        if company:
            sha = hashlib.sha512(str(company.write_date).encode("utf-8")).hexdigest()[
                :7
            ]
            return f"/web/image/{self._name}/{company_id}/favicon?unique={sha}"
        else:
            return False
