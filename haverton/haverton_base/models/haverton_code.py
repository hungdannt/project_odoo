# -*- coding: utf-8 -*-
from odoo import fields, models

CODE_TYPES = {
    'variation_reason': 'Variation Reason',
    'variation_approval': 'Variation Approval',
}


class HavertonCode(models.Model):
    _name = 'haverton.code'
    _description = 'Haverton Code'
    _inherit = 'abstract.uuid'

    name = fields.Char(required=True)
    code_number = fields.Integer(required=True)
    domain_number = fields.Integer(required=True)
    code_type = fields.Selection([
        *CODE_TYPES.items(),
    ])

    _sql_constraints = [
        (
            "code_number_domain_number_uniq",
            "unique(code_number, domain_number)",
            "This code already exists."
        )
    ]

    def browse_by_domain_and_code_number(self, domain: int, code: int):
        return self.search([('domain_number', '=', domain), ('code_number', '=', code)], limit=1)

    @property
    def variation_approval_domain(self):
        return ('code_type', '=', 'variation_approval')
