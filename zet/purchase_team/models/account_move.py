from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_team_id = fields.Many2one(
        'purchase.team', 'Purchase Team', check_company=True,
        store=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
