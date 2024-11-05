from odoo import api, fields, models, _
from odoo.exceptions import UserError


class UploadAttachFile(models.AbstractModel):
    _name = "upload.attach.file"
    _description = "Upload Attach File"

    attachment_ids = fields.Many2many('ir.attachment')
    number_attachment = fields.Integer(compute="_compute_number_attachment")
    total_file_size = fields.Integer(compute="_compute_total_file_size")

    @api.depends('attachment_ids')
    def _compute_total_file_size(self):
        for rec in self:
            rec.total_file_size = 0
            if 'order_id' in rec._fields:
                rec.total_file_size = rec.order_id.total_file_size_in_line

    @api.depends('attachment_ids')
    def _compute_number_attachment(self):
        for rec in self:
            rec.number_attachment = len(rec.attachment_ids)

    def action_get_attachment_view(self):
        return {
            "name": _('Upload File'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'upload.files.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            "context": {
                'default_res_id': self.id,
                'default_res_model': self._name,
            }
        }

    @api.constrains('attachment_ids')
    def _check_attachment_ids(self):
        config_parameter = self.env['ir.config_parameter'].sudo()
        has_limit = bool(config_parameter.get_param(
            'zet_sale_management.has_limit'))
        number_of_lines_limit = int(config_parameter.get_param(
            'zet_sale_management.number_of_lines_limit'))
        capacity_limit = int(config_parameter.get_param(
            'zet_sale_management.capacity_limit'))
        for rec in self:
            if not has_limit:
                continue
            if len(rec.attachment_ids) > number_of_lines_limit:
                message = _('Too many files have been selected. Please choose no more than %s files.', number_of_lines_limit)
                raise UserError(message)
            if rec.total_file_size * 1.00 > capacity_limit * 1048576.00:
                message = _('Your file is too large. Please try to make it smaller or split it into smaller files to proceed with the processing.')
                raise UserError(message)
