from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _check_company_auto = True

    stage_id = fields.Many2one('crm.stage', check_company=True, domain="['|',('company_id','=',False),('company_id', 'in', company_ids)]")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def init(self):
        self = self.sudo()
        crm_stage = self.env['crm.stage'].sudo()
        crm_leads = self.search([])
        for crm in crm_leads:
            if crm.company_id and crm.company_id != crm.stage_id.company_id:
                stage = crm_stage.search([('name', '=', crm.stage_id.name),('company_id', '=', crm.company_id.id)], limit=1)
                if not stage and crm.stage_id:
                    stage = crm.stage_id.copy({
                        'company_id': crm.company_id.id
                    })
                # Only update data if exist stage_id
                if stage:
                    crm.stage_id = stage.id
