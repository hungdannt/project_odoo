from odoo import api, fields, models


class MailMail(models.Model):
    _inherit = 'mail.mail'
    save_attachment = fields.Boolean()
    emg_file_name = fields.Char()
    res_model = fields.Char()
    res_id = fields.Integer()

    def send(self, auto_commit=False, raise_exception=False):
        for rec in self:
            context = {
                'save_attachment': rec.save_attachment,
                'emg_file_name': rec.emg_file_name,
                'res_model': rec.res_model,
                'res_id': rec.res_id,
            }
            super(MailMail, rec.with_context(context)).send(
                auto_commit, raise_exception)

    def prepare_new_record_values(self, values):
        fields = ['save_attachment', 'emg_file_name', 'res_model', 'res_id']
        for field in fields:
            ctx_value = self._context.get(field)
            if ctx_value:
                values[field] = ctx_value
        return values

    @api.model_create_single
    def create(self, values):
        values = self.prepare_new_record_values(values)
        res = super().create(values)
        return res
