import re
from typing import Any

from fastapi import APIRouter
from odoo import _, api, exceptions, fields, models, tools

from ..routers import router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("haverton", "Haverton Endpoint")], ondelete={"haverton": "cascade"}
    )
    auth_method = fields.Selection(
        selection=[("api_key", "Api Key"), ("http_basic", "HTTP Basic")],
        string="Authentication method",
        default='http_basic',
    )

    def _get_fastapi_routers(self) -> list[APIRouter]:
        # Add router defined for tests to the demo app
        self.ensure_one()
        routers = super()._get_fastapi_routers()
        if self.app == "haverton":
            routers.append(router)
        return routers

    @api.constrains("root_path")
    def _check_root_path(self):
        super()._check_root_path()
        for rec in self:
            if not re.fullmatch('/api/v\d+', rec.root_path):
                raise exceptions.UserError(_("Root Path must be /api/v[integer] . Ex: /api/v1"))

    def _prepare_fastapi_app_params(self) -> dict[str, Any]:
        res = super()._prepare_fastapi_app_params()
        config_parameter = self.env['ir.config_parameter'].sudo()
        api_debug = bool(config_parameter.get_param(
            'haverton_base.api_debug'))
        if not api_debug:
            # Hide the api docs in the production environment
            res["openapi_url"] = None
        return res
