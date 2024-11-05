from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = "mail.template"

    save_attachment = fields.Boolean()
