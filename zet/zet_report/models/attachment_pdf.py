from odoo import fields, models, api, _


class AttachmentPDF(models.AbstractModel):
    _name = "attachment.pdf"
    _description = "Attachment PDF"

    attachment_pdf_ids = fields.Many2many('ir.attachment', compute="_compute_attachment_pdf_ids")
    attachment_count = fields.Integer(string='Attachment Count', compute='_compute_attachment_count')
    attachment_ids = fields.Many2many('ir.attachment', compute="_compute_attachment_ids")

    def _compute_attachment_ids(self):
        pass

    @api.depends('attachment_ids')
    def _compute_attachment_pdf_ids(self):
        for rec in self:
            rec.attachment_pdf_ids = rec.attachment_ids.filtered(lambda x:x.mimetype == "application/pdf" and x.is_printed)

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    def action_select_attachments(self):
        view = self.env.ref('zet_report.upload_files_wizard_view_form', raise_if_not_found=True)
        if not view:
            return
        return {
            'name': _('Select Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'upload.files.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_attachment_ids': self.attachment_ids.ids,
                'show_checkbox': True,
            },
        }
