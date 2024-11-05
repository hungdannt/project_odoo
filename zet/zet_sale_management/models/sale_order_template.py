from odoo import _, api, fields, models


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    partner_id = fields.Many2one('res.partner', string="Customer")
    set_as_default = fields.Boolean(copy=False)
    team_id = fields.Many2one(
        'crm.team', string='Sales Team')
    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user)

    def write(self, value):
        res = super().write(value)
        for rec in self:
            if rec.set_as_default:
                rec._revoke_partner_default_template()
        return res

    def _revoke_partner_default_template(self):
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('set_as_default', '=', True),
            ('id', '!=', self.id)
        ]
        self.search(domain).write({
            'set_as_default': False
        })
