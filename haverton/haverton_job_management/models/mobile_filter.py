from odoo import _, api, exceptions, models


class MobileFilter(models.Model):
    """ Model for custom filter which used on mobile """
    _inherit = 'mobile.filter'

    @api.constrains('show_on_mobile', 'group_ids')
    def _check_total_filter_show_on_mobile_for_group_ids(self):
        dashboard_activities_filter_categories = self.env['mobile.filter.category'].search(
            [('screen_type', '=', 'dashboard_activities')])
        if any([
            not dashboard_activities_filter_categories,
            self.mobile_filter_category_id not in dashboard_activities_filter_categories
        ]):
            return
        # Check: Each Haverton user must have at least one filter item in each dashboard filter category.
        category_haverton_role = self.env.ref(
            'haverton_base.module_category_haverton_role')
        haverton_groups = self.env['res.groups'].search([
            ('category_id', '=', category_haverton_role.id)
        ])
        if not haverton_groups:
            return

        for category in dashboard_activities_filter_categories:
            if not category.mobile_filter_ids:
                continue
            for group in haverton_groups:
                general_domain = [
                    ('show_on_mobile', '=', True),
                    ('group_ids', 'in', [group.id, *group.implied_ids.ids])
                ]
                total_active_filter_items = self.search_count([
                    *general_domain,
                    ('mobile_filter_category_id', '=',
                     category.id),
                ])
                if total_active_filter_items < 1:
                    raise exceptions.UserError(
                        _('At least one item is required in the %s filter category for %s.' % (category.name, group.name)))
