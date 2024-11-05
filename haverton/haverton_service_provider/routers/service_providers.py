from typing import Annotated

from fastapi import APIRouter, Depends, Query
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import (
    authorize_session,
    format_query,
)
from odoo.addons.haverton_base_fastapi.schemas import HavertonCompliance, OrderBy
from odoo.http import request

from ..schemas import (
    ServiceProvider,
    ServiceProviderBase,
    ServiceProviderMasterData,
    ServiceProviderSearch,
    ServiceProviderSortBy,
)
from ..utils import service_provider as service_provider_utils

router = APIRouter()


@router.get("/", response_model=PagedCollection[ServiceProviderBase])
def get_service_providers(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        q: Annotated[str, Depends(format_query)] = None,
        search_field: ServiceProviderSearch = None,
        service_provider_uuids: Annotated[list[str] | None, Query()] = [],
        active: bool = None,
        contract_no: str = None,
        region_uuid: str = None,
        service_type: str = None,
        compliance: str = None,
        work_category: str = None,
        sort_by: Annotated[list[ServiceProviderSortBy] |
                           None, Query()] = [ServiceProviderSortBy.preferred_name],
        order_by: OrderBy = OrderBy.asc):
    """
    Get list of the service provider.
    Params:
    - **q**: key to search
    - **search_field**: field to search
    - **active**: status to filter
    - **contract_no**: contract_no to filter
    - **region_uuid**: uuid of region to filter
    - **service_type**: key of service_type to filter
    - **compliance**: key of compliance to filter
    - **work_category**: key of work_category to filter
    - **sort_by**: fields to sort
    - **order_by**: order to sort
    """
    domain = service_provider_utils.get_service_providers_domain(
        search_kwargs={'q': q, 'search_field': search_field},
        filter_kwargs={
            'active': active,
            'contract_no': contract_no,
            'region_uuid': region_uuid,
            'service_type': service_type,
            'work_category': work_category,
            'service_provider_uuids': service_provider_uuids,
        })
    specification = dict(ServiceProviderBase())
    specification.update({
        'service_type_ids': {'fields': {'uuid': {}, 'description': {}}},
        'compliance_id': {'fields': dict(HavertonCompliance())},
    })
    specification['service_type_ids'] = {
        'fields': {'uuid': {}, 'description': {}}}
    model = request.env['res.partner'].with_context(
        active_test=False, haverton_search=True)
    res = model.web_search_read(
        domain=domain,
        specification=specification,
        order=','.join(map(lambda i: i.value + ' ' + order_by.value, sort_by)),
    )
    paginated_records, count = service_provider_utils.paginate_and_filter_by_compliance(res['records'], paging, compliance)
    return PagedCollection[ServiceProviderBase](
        count=count,
        items=paginated_records
    )


@router.get("/masterdata", response_model=PagedCollection[dict])
def get_service_provider_masterdata(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        field_name: ServiceProviderMasterData,
        q: Annotated[str, Depends(format_query)] = None):
    """
    Get masterdata of the service provider based on the field name.
    """
    record, total = service_provider_utils.get_service_provider_masterdata(
        field_name, paging.limit, paging.offset, q)
    return PagedCollection[dict](
        count=total,
        items=record
    )


@router.get("/{uuid}", response_model=ServiceProvider)
def get_service_provider(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the service provider detail
    """
    res_partner = request.env['res.partner'].with_context(
        active_test=False).validate_by_uuid(uuid)
    return res_partner
