from odoo import _, api, exceptions, fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    task_booked_start_date = fields.Datetime()

    @api.constrains("subtype_id")
    def _check_subtype_id(self):
        for rec in self:
            booking_subtype = self.env.ref(
                'haverton_job_management.mt_booking')
            if not booking_subtype:
                continue
            if rec.subtype_id == booking_subtype and not rec.task_booked_start_date:
                raise exceptions.UserError(
                    _('The task_booked_start_date field is required in the booking message.')
                )
