from odoo.addons.haverton_base_fastapi.schemas import BaseModel
from odoo.http import request


def get_serializer(instance: object, serializer_model: BaseModel):
    if not instance or not serializer_model:
        return
    fields = serializer_model.model_fields.keys()
    vals_dict = instance.read(fields)[0]
    return serializer_model(**vals_dict)


def get_masterdata(model_name, response_field, limit, offset, domain=None, query=None, sort_by=None, order_by='ASC'):
    domain = domain or []
    model = request.env[model_name]
    if query:
        domain.append((response_field, 'ilike', query))
    records = model.with_context(haverton_search=True, active_test=False).web_search_read(
        domain=domain,
        specification={'uuid': {}, response_field: {}},
        order=(sort_by or response_field) + ' ' + order_by,
        limit=limit,
        offset=offset
    )['records']
    results = [{'key': i['uuid'], 'value': i.get(
        response_field)} for i in records]
    total = model.search_count(domain)
    return results, total
