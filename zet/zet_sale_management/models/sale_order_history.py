from odoo import models, fields


class SaleOrderHistory(models.Model):
    _name = "sale.order.history"
    _description = "History Sale Order"
    _order ="version_number desc"

    order_id = fields.Many2one('sale.order')
    version_number = fields.Char()
    name = fields.Char()
    create_date = fields.Datetime(string="Edit Time")
    user_edit = fields.Many2one('res.users', string="Editor")
    old_value = fields.Char()
    signature = fields.Image(
        string="Signature",
        copy=False, attachment=True, max_width=1024, max_height=1024)

    def get_portal_url(self):
        return f'/my/orders/history/{self.id}'

    def action_preview_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': self.get_portal_url(),
        }
