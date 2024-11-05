from datetime import datetime

from odoo.addons.haverton_base.tools.datetime import get_domain_filter_datetime_in_day
from odoo.http import request
from odoo.osv import expression

from ..schemas import TodoType
from ..utils import common as common_utils
from ..utils import job as job_utils


def get_filter_dt_start_in_todo():
    limit_years_in_todo_param = request.env['ir.config_parameter'].sudo().get_param(
        'haverton_job_management.limit_years_in_todo')
    limit_years_in_todo = int(
        limit_years_in_todo_param if limit_years_in_todo_param is not None else 1)
    start_year = datetime.now().year - limit_years_in_todo
    return datetime(start_year, 1, 1)


def get_filter_domain_todo_list(filter_kwargs: dict):
    domain = []
    haverton_task_type = filter_kwargs.get('haverton_task_type')
    if haverton_task_type:
        if haverton_task_type == TodoType.activity:
            domain += request.env['project.task'].single_activity_domain
        elif haverton_task_type != TodoType.variation:
            # variation is filtered by the child activities. So not add that domain
            domain += [('haverton_task_type', '=', haverton_task_type)]
    uuids = filter_kwargs.get('uuids')
    if uuids:
        domain.append(('uuid', 'in', uuids))

    # status filter of activities (like the get_job_activities API)
    not_completed = filter_kwargs.get('not_completed')
    booked_start = filter_kwargs.get('booked_start')
    not_confirmed = filter_kwargs.get('not_confirmed')
    # status for defect
    status = filter_kwargs.get('status')
    # filter by the user uuids
    user_uuids = filter_kwargs.get('user_uuids', [])
    # filter by contract_no (job)
    job_uuids = filter_kwargs.get('job_uuids')
    # filter by service_type/defect_type
    service_type_uuid = filter_kwargs.get('service_type_uuid')

    # handle to filter the current user tasks
    user_id = filter_kwargs.get('user_id')
    if user_id:
        if user_id.role != 'admin':
            # ignore user_uuids if the current user is not admin
            domain += [('user_id', '=', user_id.id)]
        else:
            user_uuids.append(user_id.uuid)
            filter_kwargs['user_uuids'] = user_uuids

    general_filter_domain = common_utils.get_task_general_filter_domain(
        filter_kwargs={
            'status': status,
            'user_uuids': user_uuids,
            'job_uuids': job_uuids,
            'haverton_task_type': haverton_task_type,
        }
    )
    domain = expression.AND([domain, general_filter_domain])

    if haverton_task_type == 'activity':
        activity_domain = job_utils.get_job_activities_domain(
            search_kwargs={},
            filter_kwargs={
                'not_completed': not_completed,
                'booked_start': booked_start,
                'not_confirmed': not_confirmed,
                'service_type_uuid': service_type_uuid,
            }
        )
        domain = expression.AND([domain, activity_domain])
    elif haverton_task_type == 'defect':
        defect_domain = job_utils.get_job_defects_domain(
            search_kwargs={},
            filter_kwargs={
                'service_type_uuid': service_type_uuid
            }
        )
        domain = expression.AND([domain, defect_domain])

    return domain


def get_domain_todo_list(search_kwargs={}, filter_kwargs={}):
    forecasted_start_date_begin = get_filter_dt_start_in_todo()
    haverton_task_type = filter_kwargs.get('haverton_task_type')
    domain = [
        ('date_end', '=', False),
        ('forecasted_start_date', '>=', forecasted_start_date_begin),
    ]
    if not search_kwargs and not filter_kwargs:
        return domain
    # search
    if search_kwargs.get('q'):
        domain.append(('name', 'ilike', search_kwargs['q']))

    # filter
    filter_domain = get_filter_domain_todo_list(filter_kwargs)
    domain = expression.AND([domain, filter_domain])
    if haverton_task_type == TodoType.variation:
        # variation is filtered by childs
        domain = [
            ('child_ids', 'in', request.env['project.task'].search(
                expression.AND(
                    [[('haverton_task_type', '=', 'activity')], domain])
            ).ids)
        ]
        # filter by start_date for variation
        start_date = filter_kwargs.get('start_date')
        if start_date:
            domain.extend(get_domain_filter_datetime_in_day(
                date=start_date, field_name='start_date'))
    return domain
