from fastapi import APIRouter
from odoo import models

from ..routers import router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    def _get_fastapi_routers(self) -> list[APIRouter]:
        self.ensure_one()
        routers = super()._get_fastapi_routers()
        if self.app == "haverton":
            # add router to the begin of routers to overwrite apis
            routers.insert(0, router)
        return routers
