from odoo import api, fields, models


class MobileFilterCategory(models.Model):
    _name = "mobile.filter.category"
    _description = "Mobile Filter Category"


    name = fields.Char(string="Category", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    show_on_mobile = fields.Boolean(string="Show on Mobile", default=True)
    screen_type = fields.Selection([])  # add selections in child modules
    group_ids = fields.Many2many(
        'res.groups',
        default=lambda self: self.env.ref(
            'haverton_base.haverton_base_group_site_supervisor'))
    mobile_filter_ids = fields.One2many(
        'mobile.filter', 'mobile_filter_category_id')

    group_ids_domain = fields.Binary(compute="_compute_group_ids_domain")

    @api.depends('code')
    def _compute_group_ids_domain(self):
        category_haverton_role = self.env.ref('haverton_base.module_category_haverton_role', raise_if_not_found=False)
        admin_groups = self.env.ref('haverton_base.haverton_base_group_admin', raise_if_not_found=False)
        category_domain = [('category_id', '=', category_haverton_role.id)] if category_haverton_role else []
        for rec in self:
            domain = list(category_domain)
            if rec.code == 'users' and admin_groups:
                domain.append(('id', '=', admin_groups.id))
            rec.group_ids_domain = domain

    _sql_constraints = [
        ("code_screen_type_unique", "unique(code, screen_type)",
         "Code must be unique per screen!"),
    ]
