from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
        context = {
            'save_attachment': self.save_attachment,
            'emg_file_name': self._get_emg_file_name(res_id),
            'res_model': self.model_id.model,
            'res_id': res_id,
        }
        return super(MailTemplate, self.with_context(context)).send_mail(res_id, force_send, raise_exception, email_values, notif_layout)

    def _generate_template_attachments(self, res_ids, render_fields,
                                       render_results=None):
        render_results = super()._generate_template_attachments(
            res_ids, render_fields, render_results)
        for res_id in res_ids:
            obj = self.env[self.model].browse(res_id)
            if 'images_section' in obj._fields and self == self.env.ref('haverton_job_management.mail_template_project_task_is_is_defect', raise_if_not_found=False):
                attachments = [(attachment.name, attachment.datas)
                               for attachment in obj.images_section.attach_images]
                render_results.get(res_id)['attachments'] += attachments
        return render_results

    def _get_emg_file_name(self, res_id):
        # Fotmant name job {Contract_no} (Work Release for {address}) {timestamp}.eml
        if not self.model_id:
            return False
        datetime = fields.Datetime.now().strftime('%Y%m%d%H%M%S')
        obj = self.env[self.model_id.model].browse(res_id)
        if not obj:
            return False
        if self.model_id.model == 'project.task':
            if not obj.project_id:
                return False
            if 'haverton_task_type' in obj._fields and obj['haverton_task_type'] == 'defect':
                return f"{obj.project_id.contract_no} (Work Release for {obj.project_id.address_id.subject_mail_address}) {datetime}.eml"
            elif self.id == self.env.ref('haverton_job_management.mail_template_reschedule_activity', raise_if_not_found=False).id:
                return f"Reschedule Work Release for Job {obj.project_id.contract_no} {datetime}.eml"
        elif self.model_id.model == 'survey.user_input' and self.id == self.env.ref(
                'haverton_inspection_management.mail_template_after_submit_inspection', raise_if_not_found=False).id:
            return f"Inspection {obj.name} {datetime}.eml"
        return False
