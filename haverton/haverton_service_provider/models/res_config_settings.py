from odoo import models

from ..schemas import ServiceProvider


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_show_service_provider_detail_fields(self):
        fields_tree_view = self.env.ref(
            'haverton_service_provider.ir_model_fields_view_tree_service_provider_detail')
        return self.get_action_show_detail_screen_fields(tree_view=fields_tree_view, action_name='Service Provider Detail Fields', model_name='res.partner', schema=ServiceProvider)
