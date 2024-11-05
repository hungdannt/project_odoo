from odoo import _
from odoo.exceptions import UserError
from odoo.http import request
from ..models.project_task import CONFIRMED_BOOKING_STATUSES


def validate_activity_uuid(uuid: str):
    activity = request.env['project.task'].validate_by_uuid(uuid)
    if activity.haverton_task_type != 'activity':
        raise UserError(_('This is not an activity'))
    return activity


def validate_update_job_activity_input(activity, **input_kwargs):
    if input_kwargs.get('booked_start_date', None) and not activity.booked_start_date:
        # message is required when booking an activity
        message = input_kwargs.get('message', None)
        if not message:
            raise UserError(_('The message is required when booking an activity'))


def get_activity_status_filter_domain(not_completed: bool, booked_start: bool, not_confirmed: bool):
    domain = []
    if not_completed is not None:
        if not_completed:
            domain.append(('date_end', '=', False))
        else:
            domain.append(('date_end', '!=', False))
    if booked_start is not None:
        if booked_start:
            domain.append(('booked_start_date', '!=', False))
        else:
            domain.append(('booked_start_date', '=', False))
    if not_confirmed is not None:
        if not_confirmed:
            domain.append(('booking_status', 'not in',
                           [*CONFIRMED_BOOKING_STATUSES.keys()]))
        else:
            domain.append(('booking_status', 'in',
                           [*CONFIRMED_BOOKING_STATUSES.keys()]))
    return domain
