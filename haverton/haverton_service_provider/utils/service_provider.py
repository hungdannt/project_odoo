from odoo.http import request

from ..schemas import ServiceProviderMasterData, ServiceProviderSearch


def get_service_providers_domain(search_kwargs: dict, filter_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets service providers.
    """
    domain = [('haverton_contact_type', '=', 'service_provider')]
    # search
    search_field = search_kwargs.get('search_field')
    if search_field and search_kwargs.get('q'):
        if search_field == ServiceProviderSearch.service_type:
            domain.append(
                ('service_type_ids.description', 'ilike', search_kwargs['q']))
        elif search_field == ServiceProviderSearch.name:
            domain.append(
                ('preferred_name', 'ilike', search_kwargs['q']))
        else:
            domain.append(
                (search_field.value, 'ilike', search_kwargs['q']))
    # filter
    for key, value in filter_kwargs.items():
        if value is None:
            continue
        match key:
            case 'region_uuid':
                domain.append(('region_ids.uuid', '=', value))
            case 'contract_no':
                domain.append(('task_ids.project_id.uuid', '=', value))
            case 'service_type':
                domain.append(('service_type_ids.uuid', '=', value))
            case 'compliance':
                domain.append(('compliance_id.uuid', '=', value))
            case 'work_category':
                domain.append(('work_category_ids.uuid', '=', value))
            case 'service_provider_uuids':
                if value:
                    domain.append(('service_provider.uuid', 'in', value))
            case _:
                domain.append((key, '=', value))
    return domain


def _get_service_provider_masterdata(model_name, field_name, limit, offset, query=None, domain=None):
    results = []
    domain = domain or []
    total = 0
    model = request.env[model_name]
    if query:
        domain.append((field_name, 'ilike', query))
    records = model.with_context(haverton_search=True).web_search_read(
        domain=domain,
        specification={'uuid': {}, field_name: {}},
        order=field_name + ' ASC',
        limit=limit,
        offset=offset
    )['records']
    results = results + \
        [{'key': i['uuid'], 'value': i.get(field_name)}
            for i in records]
    total = model.search_count(domain)
    return results, total


def get_service_provider_masterdata(field_name: ServiceProviderMasterData, limit: int = None, offset: int = 0, query: str = None):
    results = []
    total = 0
    match field_name:
        case ServiceProviderMasterData.region:
            # region
            results, total = _get_service_provider_masterdata(
                model_name='haverton.region', field_name='description', limit=limit, offset=offset, query=query)
        case ServiceProviderMasterData.contract_no:
            # contract_no
            results, total = _get_service_provider_masterdata(
                model_name='project.project', field_name='contract_no', limit=limit, offset=offset, query=query)
        case ServiceProviderMasterData.service_type:
            # service_type
            results, total = _get_service_provider_masterdata(
                model_name='haverton.service.type', field_name='description', limit=limit, offset=offset, query=query)
        case ServiceProviderMasterData.work_category:
            # work_category
            results, total = _get_service_provider_masterdata(
                model_name='haverton.work.category', field_name='description', limit=limit, offset=offset, query=query)
        case ServiceProviderMasterData.compliance:
            # compliance
            results, total = _get_service_provider_masterdata(
                model_name='haverton.compliance', field_name='name', limit=limit, offset=offset, query=query)
    return results, total


def paginate_and_filter_by_compliance(records, paging, compliance_uuid=None):
    if not records:
        return [], 0
    if compliance_uuid:
        records = [record for record in records if record['compliance_id']
                   ['uuid'] == compliance_uuid]
    count = len(records)
    paginated_records = records[paging.offset:paging.offset + paging.limit]
    return paginated_records, count
