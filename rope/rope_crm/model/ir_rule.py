# coding: utf-8
from odoo import api, models


class IrRule(models.Model):
    _inherit = 'ir.rule'

    def init(self):
        crm_rule_personal_lead = self.env.ref('crm.crm_rule_personal_lead', raise_if_not_found=False)
        crm_rule_personal_lead_sudo = crm_rule_personal_lead.sudo()
        crm_rule_personal_lead_sudo.perm_write = False
        crm_rule_personal_lead_sudo.perm_unlink = False
        res_partner_rule = self.env.ref('base.res_partner_rule', raise_if_not_found=False).sudo()
        res_partner_rule.domain_force = "['|', ('company_id', 'in', company_ids), ('company_id', '=', False)]"
