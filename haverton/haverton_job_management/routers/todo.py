from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
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
    CountToDoList,
    JobActivityFilterStatus,
    TodoFilterCategory,
    TodoFilterCategoryCode,
    ToDoList,
    TodoScreenType,
    TodoType,
)
from ..utils import defect as defect_utils
from ..utils import master_data as master_data_utils
from ..utils import todo as todo_utils

router = APIRouter()


@router.get("/summary", response_model=CountToDoList)
def get_todo(
    current_user: Annotated[Users | None, Depends(authorize_session)],
):
    """
    Get list of the job.
    Params:
    - **current_user**: key to search
    """
    activity_domain = todo_utils.get_domain_todo_list(
        filter_kwargs={
            'user_id': current_user,
            'haverton_task_type': TodoType.activity,
        }
    )
    defect_domain = todo_utils.get_domain_todo_list(
        filter_kwargs={
            'user_id': current_user,
            'haverton_task_type': TodoType.defect,
        }
    )
    variation_domain = todo_utils.get_domain_todo_list(
        filter_kwargs={
            'user_id': current_user,
            'haverton_task_type': TodoType.variation,
        }
    )
    total_activities = request.env['project.task'].with_context(haverton_search=True).search_count(
        domain=activity_domain
    )
    total_defects = request.env['project.task'].with_context(haverton_search=True).search_count(
        domain=defect_domain
    )
    total_variants = request.env['project.task'].with_context(haverton_search=True).search_count(
        domain=variation_domain
    )
    return {
        'total_activities': total_activities,
        'total_defects': total_defects,
        'total_variants': total_variants
    }


@router.get("/filter_categories", response_model=dict)
def get_todo_filter_categories(current_user: Annotated[Users | None, Depends(authorize_session)]):
    """
    Get list of the todo filter category belong current_user.
    """
    todo_filter_categories = request.env['mobile.filter.category'].search([
        ('screen_type', 'in', list(TodoScreenType)),
        ('group_ids', 'in', current_user.haverton_group_ids.ids),
        ('show_on_mobile', '=', True)
    ]).grouped('screen_type')
    result = {}
    for key, value in todo_filter_categories.items():
        result[key] = [TodoFilterCategory(**rec) for rec in value.read()]
    return result


@router.get("/masterdata", response_model=PagedCollection[dict])
def get_todo_masterdata(
    paging: Annotated[Paging, Depends(paging)],
    current_user: Annotated[Users | None, Depends(authorize_session)],
    category_code: TodoFilterCategoryCode,
    q: Annotated[str, Depends(format_query)] = None,
):
    """
    Get masterdata of the todo filters on the user.
    - **category_code**: str. Choose one of below:
        + **users** : list of users
        + **contract_no** : list of the job's contract_no
        + **service_type** : list of the service type / defect type
    """
    res_model, res_field = master_data_utils.get_todo_masterdata_info(
        category_code)
    if not res_model:
        return PagedCollection[dict](
            count=0,
            items=[]
        )
    domain = [('haverton_uuid', '!=', False)]
    if category_code == TodoFilterCategoryCode.users:
        domain = request.env['res.users'].haverton_active_domain
    record, total = master_data_utils.get_masterdata(
        res_model, res_field, paging.limit, paging.offset, domain=domain, query=q)
    return PagedCollection[dict](
        count=total,
        items=record
    )


@router.get("/{haverton_task_type}", response_model=PagedCollection[ToDoList])
def get_todo_list(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        haverton_task_type: TodoType = TodoType.variation,
        uuids: Annotated[list[str] | None, Query()] = [],
        q: Annotated[str, Depends(format_query)] = None,
        # status filter of activities (like the get_job_activities API)
        not_completed: bool = None,  # stage
        booked_start: bool = None,  # booked_start_date
        not_confirmed: bool = None,  # booking_status
        # status for defect
        status: Annotated[list[JobActivityFilterStatus] | None, Query()] = [],
        # filter by the user uuids
        user_uuids: Annotated[list[str] | None, Query()] = [],
        # filter by contract_no (job)
        job_uuids: Annotated[list[str] | None, Query()] = [],
        # filter by service_type/defect_type
        service_type_uuid: str = None,
        start_date: int = None,
        order_by: OrderBy = OrderBy.asc):
    """
    Get list of the job.
    Params:
    - **q**: key to search
    - **haverton_task_type**: search in type activity
    - **order_by**: order to sort
    - **uuids**: list of the task uuids to filter
    - **not_completed**: filter status in the activities screen
    - **booked_start**: filter status in the activities screen
    - **not_confirmed**: filter status in the activities screen
    - **status**: filter status in the defects screen
    - **user_uuids**: list of the user uuids to filter
    - **job_uuids**: list of the uuids of contract_no (job) to filter
    - **service_type_uuid**: filter service_type in the activities screen / filter defect_type in the defects screen
    - **start_date**: timestamp of the start_date to filter
    """
    if start_date:
        start_date = datetime.fromtimestamp(start_date).date()
    domain = todo_utils.get_domain_todo_list(
        search_kwargs={'q': q},
        filter_kwargs={
            'user_id': current_user,
            'haverton_task_type': haverton_task_type,
            'uuids': uuids,
            'not_completed': not_completed,
            'booked_start': booked_start,
            'not_confirmed': not_confirmed,
            'user_uuids': user_uuids,
            'job_uuids': job_uuids,
            'service_type_uuid': service_type_uuid,
            'start_date': start_date,
        }
    )
    specification = dict(ToDoList())
    specification['service_type'] = {'fields': {'uuid': {}, 'description': {}}}
    specification['approval_id'] = {'fields': {'name': {}}}
    specification['reason_id'] = {'fields': {'name': {}}}
    specification['project_id'] = {'fields': {'uuid': {}, 'contract_no': {}}}
    specification['address_id'] = {'fields': {'uuid': {}, 'name': {}, 'site_address': {}}}
    if haverton_task_type == 'defect':
        res = request.env['project.task'].with_context(haverton_search=True).web_search_read(
            domain=domain,
            specification=specification,
            order='forecasted_start_date ' + order_by.value
        )
        res['records'], count = defect_utils.paginate_and_filter_by_status(res['records'], paging, status)
    else:
        res = request.env['project.task'].with_context(haverton_search=True).web_search_read(
            domain=domain,
            specification=specification,
            order='forecasted_start_date ' + order_by.value,
            limit=paging.limit,
            offset=paging.offset
        )
        count = request.env['project.task'].search_count(domain=domain)
    return PagedCollection[ToDoList](
        count=count,
        items=res['records']
    )
