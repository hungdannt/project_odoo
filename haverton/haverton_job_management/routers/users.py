from typing import Annotated

from fastapi import APIRouter, Depends, Query
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import (
    authorize_session,
    format_query,
)
from odoo.addons.haverton_base_fastapi.schemas import FilterItem, OrderBy
from odoo.http import request
from odoo.osv import expression

from ..schemas import (
    DashboardActivity,
    DashboardActivityFilterCategory,
    DashboardActivityFilterStatus,
    DashboardActivityFilterTimePeriod,
)
from ..utils import user as user_utils

router = APIRouter()


@router.get("/me/dashboard/summary")
def get_dashboard_summary(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    date_start: int,
    date_end: int,
):
    """
    Get the summary details of the dashboard.
    - **date_start**: timestamp of the date_start to filter
    - **date_end**: timestamp of the date_end to filter
    """
    response = dict()
    domain = user_utils._get_dashboard_activities_domain(current_user)
    task_model = request.env['project.task']
    pending_domain = expression.AND([domain, user_utils.get_dashboard_activity_filter_domain(
        status=DashboardActivityFilterStatus.pending, date_start=date_start, date_end=date_end)])
    due_domain = expression.AND([domain, user_utils.get_dashboard_activity_filter_domain(
        status=DashboardActivityFilterStatus.due_activities, date_start=date_start, date_end=date_end)])
    overdue_domain = expression.AND([domain, user_utils.get_dashboard_activity_filter_domain(
        status=DashboardActivityFilterStatus.overdue, date_start=date_start, date_end=date_end)])

    total_pending_activities = task_model.search_count(pending_domain)
    total_due_activities = task_model.search_count(due_domain)
    total_overdue_activities = task_model.search_count(overdue_domain)
    response['total_due_activities'] = total_due_activities
    response['total_overdue_activities'] = total_overdue_activities
    response['total_activities'] = total_pending_activities + \
        total_due_activities + total_overdue_activities
    return response


@router.get("/me/dashboard/activities", response_model=PagedCollection[DashboardActivity])
def get_dashboard_activities(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        date_start: int,
        date_end: int,
        status: DashboardActivityFilterStatus = None,
        q: Annotated[str, Depends(format_query)] = None,
        activity_uuids: Annotated[list[str] | None, Query()] = [],
        order_by: OrderBy = OrderBy.asc):
    """
        Get the dashboard activities.
        - **activity_uuids**: list of the activity uuid to filter
        - **date_start**: timestamp of the date_start to filter
        - **date_end**: timestamp of the date_end to filter
    """
    domain = user_utils.get_dashboard_activities_domain(
        current_user, query=q, filter_kwargs={'activity_uuids': activity_uuids, 'status': status, 'date_start': date_start, 'date_end': date_end})
    specification = dict(DashboardActivity())
    specification['project_id'] = {'fields': {'uuid': {}}}
    specification['address_id'] = {
        'fields': {'uuid': {}, 'name': {}, 'site_address': {}}
    }
    res = request.env['project.task'].with_context(haverton_search=True, dashboard_filter_date_start=date_start, dashboard_filter_date_end=date_end).web_search_read(
        domain=domain,
        specification=specification,
        limit=paging.limit,
        offset=paging.offset,
        order='name ' + order_by.value
    )
    count = request.env['project.task'].with_context(
        haverton_search=True).search_count(domain=domain)
    return PagedCollection[DashboardActivity](
        count=count,
        items=res['records']
    )


@router.get("/me/dashboard/masterdata", response_model=dict)
def get_job_masterdata(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    mobile_filter_categories: Annotated[
        list[DashboardActivityFilterCategory] | None, Query()] = None
):
    """
    Get masterdata for the dashboard activities filter.
    Params:
    - **mobile_filter_categories** : List of the filter_category_code. Includes: status, time_period.
                                  if not mobile_filter_categories, return all data of all category
    """
    domain = [
        ('group_ids', 'in', current_user.haverton_group_ids.ids),
        ('show_on_mobile', '=', True)
    ]
    if mobile_filter_categories:
        domain.append(('mobile_filter_category_code',
                      'in', mobile_filter_categories))
    dashboard_activity_filter_items = request.env['mobile.filter'].search(
        domain).grouped('mobile_filter_category_code')
    result = {}
    for key, value in dashboard_activity_filter_items.items():
        result[key] = [FilterItem(**rec) for rec in value.read()]
    return result
