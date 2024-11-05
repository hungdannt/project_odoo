from odoo import api, fields, models


class HavertonRegion(models.Model):
    _name = 'haverton.region'
    _description = 'Haverton Region'
    _inherit = 'abstract.uuid'
    _rec_name = 'description'

    name = fields.Char(compute='_compute_name', store=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('haverton.region')
    is_default_job_region = fields.Boolean(default=False)
    is_default_service_provider_region = fields.Boolean(default=False)

    @api.depends('parent_id', 'parent_id.description', 'description')
    def _compute_name(self):
        for rec in self:
            name = rec.description
            if rec.parent_id:
                name = rec.parent_id.description + ' / ' + name
            rec.name = name
