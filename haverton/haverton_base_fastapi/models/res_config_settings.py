from odoo import models

from ..schemas import BaseModel, User


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def get_action_show_detail_screen_fields(self, tree_view, action_name: str, model_name: str, schema: BaseModel):
        """
        Params:
        - tree_view: The tree view of action
        - action_name: The name of action
        - model_name: The name of model which is setted the fields
        - schema: The return pydantic model in the schemas
        """
        if not tree_view:
            return
        fields_hidden = schema.fields_required.fget(schema)
        deprecated_fields = [
            name for (name, info) in schema.model_fields.items() if info.deprecated]
        if deprecated_fields:
            fields_hidden.extend(deprecated_fields)
        return {
            'name': action_name,
            'domain': [('model_id.model', '=', model_name), ('name', 'in', list(schema.model_fields.keys())), ('name', 'not in', fields_hidden)],
            'res_model': 'ir.model.fields',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [[tree_view.id, 'tree']],
            'context': {},
            'target': 'new',
        }

    def action_show_profile_fields(self):
        fields_tree_view = self.env.ref(
            'haverton_base_fastapi.ir_model_fields_view_tree_profile')
        return self.get_action_show_detail_screen_fields(tree_view=fields_tree_view, action_name='Profile Fields', model_name='res.users', schema=User)
