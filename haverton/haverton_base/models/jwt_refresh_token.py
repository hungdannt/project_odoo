from datetime import datetime

from odoo import api, fields, models


class JwtRefreshToken(models.Model):
    _name = 'jwt.refresh.token'
    _description = 'Store Refresh Token Belong A User'

    refresh_token = fields.Char(required=True)
    user_id = fields.Many2one(
        'res.users', string='User', required=True, ondelete='cascade')
    user_login = fields.Char(related='user_id.login')
    expire_at = fields.Datetime(default=None)
    is_expired = fields.Boolean(compute='_compute_is_expired')

    _sql_constraints = [
        (
            "refresh_token_unique",
            "unique(refresh_token)",
            "Refresh refresh_token is existed.",
        )
    ]

    @api.depends('expire_at')
    def _compute_is_expired(self):
        for rec in self:
            if rec.expire_at:
                rec.is_expired = datetime.now() > rec.expire_at
            else:
                rec.is_expired = False
