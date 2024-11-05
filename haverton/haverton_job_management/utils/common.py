def get_task_general_filter_domain(filter_kwargs):
    """
    Get the filter domain based on the general fields
    """
    domain = []
    status = filter_kwargs.get('status')
    user_uuids = filter_kwargs.get('user_uuids')
    job_uuids = filter_kwargs.get('job_uuids')
    service_type_uuid = filter_kwargs.get('service_type_uuid')
    regions = filter_kwargs.get('regions')

    if status:
        domain.append(('status', 'in', status))
    if user_uuids:
        domain.append(('user_id.uuid', 'in', user_uuids))
    if job_uuids:
        domain.append(('project_id.uuid', 'in', job_uuids))
    if regions:
        domain.append(('project_id.region_id', 'in', regions))
    if service_type_uuid:
        domain.append(('defect_type_id.uuid', '=', service_type_uuid))
    return domain
