from odoo import models

from ..schemas import User


class ResUsers(models.Model):
    _inherit = 'res.users'

    @property
    def haverton_updatable_fields(self):
        return set(User.model_fields.keys())
