from odoo import api, fields, models


class MobileFilter(models.Model):
    """ Model for custom filter which used on mobile """
    _name = 'mobile.filter'
    _description = 'Mobile Filter'

    def _get_group_ids_domain(self):
        category_haverton_role = self.env.ref(
            'haverton_base.module_category_haverton_role')
        if category_haverton_role:
            return [('category_id', '=', category_haverton_role.id)]
        return []

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    show_on_mobile = fields.Boolean(default=True)
    mobile_filter_category_id = fields.Many2one(
        'mobile.filter.category', required=True)
    mobile_filter_category_code = fields.Char(
        related='mobile_filter_category_id.code', store=True)
    mobile_filter_category_name = fields.Char(
        related='mobile_filter_category_id.name', store=True)
    screen_type = fields.Selection(
        related='mobile_filter_category_id.screen_type', store=True)
    filter_domain = fields.Char(compute='_compute_filter_domain')
    group_ids = fields.Many2many(
        'res.groups',
        default=lambda self: self.env.ref(
            'haverton_base.haverton_base_group_site_supervisor'),
        domain=_get_group_ids_domain)

    _sql_constraints = [
        ("code_mobile_filter_category_id_unique",
         "unique(code, mobile_filter_category_id)", "Code must be unique per category!"),
    ]

    @api.depends('mobile_filter_category_id')
    def _compute_filter_domain(self):
        """
        Overwrite this function in the child modules
        """
        for record in self:
            record.filter_domain = None
