from odoo import models


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    @property
    def default_groups(self):
        res = super().default_groups
        res.extend([
            'survey.group_survey_manager',
            'project.group_project_manager',
        ])
        return res
