from typing import Annotated

from fastapi import APIRouter, Depends
from odoo import Command, _
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import (
    authorize_session,
    format_query,
)
from odoo.addons.haverton_base_fastapi.schemas import (
    Message,
    MessageCreateWithAttachment,
    OrderBy,
)
from odoo.addons.haverton_base_fastapi.utils import message as base_message_utils
from odoo.exceptions import UserError
from odoo.http import request

from ..schemas import (
    JobMessageBase,
    JobMessageSubtypeCode,
    JobVariation,
    JobVariationActivity,
    VariationMasterData,
)
from ..utils import master_data as master_data_utils
from ..utils import message as message_utils
from ..utils import variation as variation_utils

router = APIRouter()


@router.get("/masterdata", response_model=PagedCollection[dict])
def get_variation_masterdata(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        field_name: VariationMasterData,
        q: Annotated[str, Depends(format_query)] = None):
    """
    Get masterdata of the variation based on the field name.
    """
    masterdata_model = getattr(request.env['project.task'], field_name.value)
    records = []
    total = 0
    if masterdata_model is not None:
        domain = master_data_utils.get_masterdata_domain(
            search_kwargs={'q': q, 'search_field': 'name'})
        if field_name == VariationMasterData.approval_id:
            domain.append(masterdata_model.variation_approval_domain)
            records, total = master_data_utils.get_masterdata(
                masterdata_model._name, 'name', paging.limit, paging.offset, domain)
    return PagedCollection[dict](
        count=total,
        items=records
    )


@router.get("/{uuid}", response_model=JobVariation)
def get_variation(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the variation detail
    """
    variation = request.env['project.task'].validate_by_uuid(uuid)
    if variation.haverton_task_type != 'variation':
        raise UserError(_('This is not a variation'))
    return variation


@router.get("/{uuid}/activities", response_model=PagedCollection[JobVariationActivity])
def get_variation_activities(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        paging: Annotated[Paging, Depends(paging)],
        uuid: str,
        q: Annotated[str, Depends(format_query)] = None,
        order_by: OrderBy = OrderBy.asc):
    """
    Get the variation activities list
    """
    variation = request.env['project.task'].validate_by_uuid(uuid)
    if variation.haverton_task_type != 'variation':
        raise UserError(_('This is not a variation'))
    domain = [('parent_id', '=', variation.id), ('name', 'ilike', q),
              ('haverton_task_type', '=', 'activity')]
    specification = dict(JobVariationActivity())
    specification['service_type'] = {'fields': {'uuid': {}, 'description': {}}}
    res = request.env['project.task'].with_context(haverton_search=True).sudo().web_search_read(
        domain=domain,
        specification=specification,
        order='reference ' + order_by.value,
        limit=paging.limit,
        offset=paging.offset
    )
    count = request.env['project.task'].sudo().search_count(domain=domain)
    return PagedCollection[JobVariationActivity](
        count=count,
        items=res['records']
    )


@router.get("/{uuid}/messages", response_model=PagedCollection[JobMessageBase])
def get_variation_messages(
    paging: Annotated[Paging, Depends(paging)],
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    variation = variation_utils.validate_variation_uuid(uuid)
    return message_utils.get_messages(variation.id, paging.limit, paging.offset)


@router.post("/{uuid}/messages", response_model=Message)
def add_new_variation_message(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str,
    payload: MessageCreateWithAttachment,
):
    variation = variation_utils.validate_variation_uuid(uuid)
    return base_message_utils.add_new_message(payload, res_object=variation, subtype_code=JobMessageSubtypeCode.note)
