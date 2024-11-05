import base64

from odoo.addons.haverton_base_fastapi.dependencies import authorize_session
from odoo.http import request
from odoo.osv import expression

from ..schemas import JobFilterJobStatusGroup, JobFilterStatus
from ..utils import activity as activity_utils

APPROVALS_CODE_MAPPING = {
    'pending': 0,
    'accepted': 1,
    'declined': 2,
    'cancelled': 3,
    'requested_by_customers': 4,
    'requested': 5,
    'completed': 6
}


def get_jobs_domain(search_kwargs: dict, filter_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets jobs.
    """
    domain = []
    # search
    if search_kwargs.get('search_field') and search_kwargs.get('q'):
        domain.append(
            (search_kwargs['search_field'].value, 'ilike', search_kwargs['q']))

    # filter by user
    user_uuids = filter_kwargs.get('user_uuids')
    current_user = authorize_session()
    if current_user.role == 'admin' and user_uuids:
        domain.append(('task_ids.user_id.uuid', 'in', user_uuids))
    else:
        domain.append(('task_ids.user_id', '=', current_user.id))

    # filter by job_uuids
    job_uuids = filter_kwargs.get('job_uuids')
    if job_uuids:
        domain.append(('uuid', 'in', job_uuids))

    # filter by job_status
    job_status = filter_kwargs.get('job_status')
    if job_status:
        domain.append(('stage_id.uuid', 'in', extract_job_status(job_status)))

    projects = request.env['project.project'].search(domain)
    if user_uuids:
        users = request.env['res.users'].browse_by_uuids(user_uuids)
    else:
        users = [current_user]

    # filter by status
    status = filter_kwargs.get('status')
    filter_ids = []
    if all([
            JobFilterStatus.completed in status,
            JobFilterStatus.incompleted in status]):
        filter_ids += [
            rec.id for rec in projects
        ]
    elif JobFilterStatus.completed in status:
        filter_ids += [
            rec.id for rec in projects if rec.check_project_is_completed_by_users(users)
        ]
    elif JobFilterStatus.incompleted in status:
        filter_ids += [
            rec.id for rec in projects if not rec.check_project_is_completed_by_users(users)
        ]

    return [('id', 'in', filter_ids)]

def get_job_activities_domain(search_kwargs: dict, filter_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets the job activities.
    """
    domain = []
    # search
    if search_kwargs.get('q'):
        domain.append(('name', 'ilike', search_kwargs['q']))
    # filter
    not_completed = filter_kwargs.get('not_completed')
    booked_start = filter_kwargs.get('booked_start')
    not_confirmed = filter_kwargs.get('not_confirmed')
    domain.extend(activity_utils.get_activity_status_filter_domain(
        not_completed=not_completed,
        booked_start=booked_start,
        not_confirmed=not_confirmed,
    ))
    sequence = filter_kwargs.get('sequence')
    user_uuids = filter_kwargs.get('user_uuids')
    activity_uuids = filter_kwargs.get('activity_uuids')
    if sequence:
        domain = expression.AND([
            domain,
            [('sequence', '=', sequence)]
        ])
    if user_uuids:
        domain.append(('user_id.uuid', 'in', user_uuids))
    if activity_uuids:
        domain.append(('uuid', 'in', activity_uuids))
    service_type_uuid = filter_kwargs.get('service_type_uuid')
    if service_type_uuid:
        domain.append(('service_type.uuid', '=', service_type_uuid))
    return domain


def get_job_defects_domain(search_kwargs: dict, filter_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets the job activities.
    """
    domain = []
    # search
    if search_kwargs.get('q'):
        domain.append(('name', 'ilike', search_kwargs['q']))
    # filter
    service_type_uuid = filter_kwargs.get('service_type_uuid')
    if service_type_uuid:
        domain.append(('defect_type_id.uuid', '=', service_type_uuid))
    defect_uuids = filter_kwargs.get('defect_uuids')
    if defect_uuids:
        domain.append(('uuid', 'in', defect_uuids))
    return domain


def get_job_variations_domain(search_kwargs: dict, filter_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets the job activities.
    """
    domain = []
    # search
    if search_kwargs.get('q'):
        domain.append(('name', 'ilike', search_kwargs['q']))
    # filter
    all_approvals = filter_kwargs.get('all_approvals')
    list_approvals = filter_kwargs.get('list_approvals')
    if not all_approvals and list_approvals:
        domain.append(('approval_id.code_number', 'in', [
                      APPROVALS_CODE_MAPPING[status] for status in list_approvals]))
    variation_uuids = filter_kwargs.get('variation_uuids')
    if variation_uuids:
        domain.append(('uuid', 'in', variation_uuids))
    return domain


def create_attachment(attach_files, model_name):
    attachment_vals = [
        {
            'name': file.filename,
            'datas': base64.b64encode(file.file.read()),
            'type': 'binary',
            'res_model': model_name,
        }
        for file in attach_files
    ]
    if attachment_vals:
        attachments = request.env['ir.attachment'].create(attachment_vals)
        return attachments
    return False


def extract_job_status(job_status: list[JobFilterJobStatusGroup | str] = None):
    status_uuids = [i for i in job_status if i not in list(
        JobFilterJobStatusGroup)]
    domain = None
    if JobFilterJobStatusGroup.active_workflows in job_status:
        domain = [('is_active_workflow', '=', True)]
    elif JobFilterJobStatusGroup.inactive_workflows in job_status:
        domain = [('is_active_workflow', '=', False)]
    elif JobFilterJobStatusGroup.any_workflows in job_status:
        domain = []
    if domain is not None:
        status_uuids += [i['uuid']
                         for i in request.env['project.project.stage'].search_read(domain, ['uuid'])]
    return list(set(status_uuids))
