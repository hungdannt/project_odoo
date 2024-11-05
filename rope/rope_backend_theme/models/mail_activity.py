# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class MailActivity(models.Model):
    _inherit = 'mail.activity'
    
    @api.model
    def create(self, vals):
        activity = super(MailActivity, self).create(vals)
        self.env['bus.bus']._sendone(activity.user_id.partner_id, 'mail.activity/updated', {'activity_created': True})
        return activity

    def write(self, vals):
        activity = super(MailActivity, self).write(vals)
        self.env['bus.bus']._sendone(self.user_id.partner_id, 'mail.activity/updated', {'activity_created': False})
        return activity

    def unlink(self):
        self.env['bus.bus']._sendone(self.user_id.partner_id, 'mail.activity/updated', {'activity_deleted': True})
        return super().unlink()
