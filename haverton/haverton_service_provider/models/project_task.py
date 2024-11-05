from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    service_provider_id = fields.Many2one('res.partner',
                                          domain="[('haverton_contact_type', '=', 'service_provider'), '|', "
                                                 "('company_id', '=?', company_id),"
                                                 "('company_id', '=', False)]")
