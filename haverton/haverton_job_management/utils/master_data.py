from odoo.http import request

from ..schemas import DefectMasterData, JobMasterDataField, TodoFilterCategoryCode


def get_masterdata_field_name(master_field: DefectMasterData):
    if master_field == DefectMasterData.service_type:
        return 'description'
    elif master_field == DefectMasterData.service_provider_id:
        return 'preferred_name'
    else:
        return 'name'


def get_masterdata(model_name, field_name, limit, offset, domain=None, query=None, sort_by=None):
    domain = domain or []
    model = request.env[model_name]
    if query:
        domain.append((field_name, 'ilike', query))
    records = model.with_context(haverton_search=True, active_test=False).web_search_read(
        domain=domain,
        specification={'uuid': {}, field_name: {}},
        order=(sort_by or field_name) + ' ASC',
        limit=limit,
        offset=offset
    )['records']
    results = [{'key': i['uuid'], 'value': i.get(field_name)} for i in records]
    total = model.search_count(domain)
    return results, total


def get_masterdata_domain(search_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets masterdata.
    """
    domain = []
    # search
    if search_kwargs.get('search_field') and search_kwargs.get('q'):
        domain.append(
            (search_kwargs['search_field'], 'ilike', search_kwargs['q']))
    return domain


def get_job_masterdata_info(master_field):
    res_model = None
    res_field = 'name'
    match master_field:
        case JobMasterDataField.user:
            res_model = 'res.users'
        case JobMasterDataField.workflow_status:
            res_model = 'project.project.stage'
    return res_model, res_field


def get_todo_masterdata_info(category_code):
    res_model = None
    res_field = 'name'
    match category_code:
        case TodoFilterCategoryCode.users:
            res_model = 'res.users'
        case TodoFilterCategoryCode.contract_no:
            res_model = 'project.project'
            res_field = 'contract_no'
        case TodoFilterCategoryCode.service_type:
            res_model = 'haverton.service.type'
            res_field = 'description'
    return res_model, res_field
