from odoo import fields, models,api

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def systray_get_activities(self):
        res = super(Users, self).systray_get_activities()
        model_ids = self.env['ir.model'].search([('custome_icon', '!=', False)])
        model_dict = {model.model: '/web/image?model=ir.model&id=%s&field=custome_icon' % model.id for model in model_ids}
        for r in res:
            icon = model_dict.get(r.get('model'))
            if icon:
                r['icon'] = icon
        return res
    