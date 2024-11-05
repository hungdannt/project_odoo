from odoo import api, fields, models


class UploadFilesWizard(models.TransientModel):
    _name = 'upload.files.wizard'
    _description = 'Upload Files Wizard'

    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments', compute="_compute_attachment_ids", inverse="_set_attachment_ids")
    res_id = fields.Integer()
    res_model = fields.Char()

    @api.depends('res_id', 'res_model')
    def _compute_attachment_ids(self):
        for rec in self:
            rec.attachment_ids = False
            obj = self.env[rec.res_model].browse(rec.res_id)
            if 'attachment_ids' in obj._fields:
                rec.attachment_ids = obj.attachment_ids

    def _set_attachment_ids(self):
        obj = self.env[self.res_model].browse(self.res_id)
        if 'attachment_ids' in obj._fields:
            obj.attachment_ids = self.attachment_ids
