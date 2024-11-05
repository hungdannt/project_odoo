from fastapi import APIRouter
from odoo import models

from ..routers import router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    def _get_fastapi_routers(self) -> list[APIRouter]:
        self.ensure_one()
        routers = super()._get_fastapi_routers()
        if self.app == "haverton":
            routers.append(router)
        return routers
