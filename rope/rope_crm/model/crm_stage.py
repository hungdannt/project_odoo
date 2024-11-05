from odoo import models, fields


class CrmStage(models.Model):
    _inherit = 'crm.stage'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
