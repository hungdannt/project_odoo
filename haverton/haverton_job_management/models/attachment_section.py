# -*- coding: utf-8 -*-
from odoo import fields, models


class AttachmentSection(models.Model):
    _name = 'attachment.section'
    _description = 'Attachment Section'
    _inherit = 'abstract.uuid'

    description = fields.Char()
    attach_images = fields.Many2many('ir.attachment', string="Attach Images")
    task_id = fields.Many2one('project.task', string='Task')
