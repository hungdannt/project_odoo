from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    attach_on = fields.Datetime()
    haverton_created_by = fields.Many2one('res.users')
    is_sent_to_client = fields.Boolean()
    is_sent_to_service_provider = fields.Boolean()
    is_available_offline = fields.Boolean()
    haverton_document_type = fields.Char()

