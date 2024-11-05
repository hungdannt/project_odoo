from odoo import fields, models, api


class AccountMoveBank(models.Model):
    _name = "account.move.bank"
    
    name = fields.Char(translate=True)
    code = fields.Char()
    
    @api.depends('name', 'code')
    def name_get(self):
        return [(record.id, f"{record.name or ''} {record.code or ''}") for record in self]
