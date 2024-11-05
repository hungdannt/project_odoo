from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    security_ids = fields.Many2many(
        'res.partner.security', 'tag_security_ids_res_partner')
    user_security_ids = fields.Many2many('res.partner.security', compute="_compute_user_security_ids")

    @api.depends_context("uid")
    def _compute_user_security_ids(self):
        for rec in self:
            user = self.env.user
            rec.user_security_ids = user.security_ids
            if user.has_group('zet_purchase.group_purchase_user_all_documents') or user.has_group('sales_team.group_sale_salesman_all_leads'):
                rec.user_security_ids = rec.user_security_ids.search([]) 

    def write(self, value):
        records = super().write(value)
        if not self._context.get('update_security_in_user'):
            self.with_context(
                update_security_in_user=True)._update_security_in_user()
        return records

    def _update_security_in_user(self):
        security_ids = self.security_ids + self.env.user.security_ids
        self.env.user.partner_id.security_ids = security_ids
