from typing import Annotated

from fastapi import APIRouter, Depends, Query
from odoo import _, fields
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import (
    authorize_session,
    format_query,
)
from odoo.addons.haverton_base_fastapi.schemas import OrderBy
from odoo.http import request

from ..schemas import (
    InspectionBase,
    InspectionStatus
)
from ..utils import inspection as inspection_utils

router = APIRouter()


@router.get("/me/inspections", response_model=PagedCollection[InspectionBase])
def get_inspections(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        q: Annotated[str, Depends(format_query)] = None,
        order_by: OrderBy = OrderBy.asc,
        uuids: Annotated[list[str] | None, Query()] = [],
        status: InspectionStatus = None,
        overdue: bool = False):
    domain = [('user_id.uuid', '=', current_user.uuid)]
    domain += inspection_utils.get_inspections_domain(
        search_kwargs={'q': q},
        filter_kwargs={
            'overdue': overdue,
            'status': status,
            'uuids': uuids,
        })

    res = request.env['survey.user_input'].with_context(haverton_search=True).web_search_read(
        domain=domain,
        specification=dict(InspectionBase()),
        order='state DESC, name ' + order_by.value,
        limit=paging.limit,
        offset=paging.offset
    )
    count = request.env['survey.user_input'].search_count(domain=domain)
    return PagedCollection[InspectionBase](
        count=count,
        items=res['records']
    )
