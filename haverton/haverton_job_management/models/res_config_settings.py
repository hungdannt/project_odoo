from odoo import fields, models

from ..schemas import Defect, Job, JobActivity, JobVariation


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    limit_years_in_todo = fields.Integer(
        config_parameter='haverton_job_management.limit_years_in_todo')

    days_until_task_start_reminder = fields.Integer(
        config_parameter='haverton_job_management.days_until_task_start_reminder', default=2)

    def action_show_job_detail_fields(self):
        fields_tree_view = self.env.ref(
            'haverton_job_management.ir_model_fields_view_tree_job_detail')
        return self.get_action_show_detail_screen_fields(tree_view=fields_tree_view, action_name='Job Detail Fields', model_name='project.project', schema=Job)

    def action_show_defect_detail_fields(self):
        fields_tree_view = self.env.ref(
            'haverton_job_management.ir_model_fields_view_tree_defect_detail')
        return self.get_action_show_detail_screen_fields(tree_view=fields_tree_view, action_name='Defect Detail Fields', model_name='project.task', schema=Defect)

    def action_show_activity_detail_fields(self):
        fields_tree_view = self.env.ref(
            'haverton_job_management.ir_model_fields_view_tree_activity_detail')
        return self.get_action_show_detail_screen_fields(tree_view=fields_tree_view, action_name='Activity Detail Fields', model_name='project.task', schema=JobActivity)

    def action_show_variation_detail_fields(self):
        fields_tree_view = self.env.ref(
            'haverton_job_management.ir_model_fields_view_tree_variation_detail')
        return self.get_action_show_detail_screen_fields(tree_view=fields_tree_view, action_name='Variation Detail Fields', model_name='project.task', schema=JobVariation)

    def action_show_dashboard_activity_filter(self):
        dashboard_activity_filter_tree_view = self.env.ref(
            'haverton_job_management.mobile_filter_view_tree', raise_if_not_found=True)
        screen_type = self._context.get('screen_type')
        if screen_type == 'dashboard_activities':
            return {        
                'name': 'Dashboard Filter Items',
                'domain': [('show_on_mobile', 'in', [True, False]), ('screen_type', '=', screen_type)],
                'res_model': 'mobile.filter',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'views': [[dashboard_activity_filter_tree_view.id, 'tree']],
                'context': {'search_default_group_by_category': 1},
                'target': 'new',
            }
        return
    
    def action_show_config_todo_filter_category(self):
        tree_view = self.env.ref(
            'haverton_job_management.mobile_filter_category_view_tree', raise_if_not_found=True)
        screen_type = self._context.get('screen_type')
        if screen_type in ['todo_defects', 'todo_activities', 'todo_variations']:
            return {        
                'name': f'Category Filter of {screen_type.replace("_", " ").title()}',
                'domain': [('show_on_mobile', 'in', [True, False]), ('screen_type', '=', screen_type)],
                'res_model': 'mobile.filter.category',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'views': [[tree_view.id, 'tree']],
                'context': {},
                'target': 'new',
            }
        return
