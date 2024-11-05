from datetime import datetime, timedelta

from odoo.addons.haverton_base.tools.datetime import get_date_range_in_week
from odoo.http import request
from odoo.osv import expression

from ..schemas import DashboardActivityFilterStatus, DashboardActivityFilterTimePeriod
from .todo import get_filter_dt_start_in_todo


def _get_dashboard_activities_domain(current_user):
    """
    Returns the domain to use to filter activities of current_user in the dashboard summary.
    """
    if not current_user:
        return []
    dt_start = get_filter_dt_start_in_todo()
    return [
        *request.env['project.task'].single_activity_domain,
        ('user_id', '=', current_user.id),
        ('date_end', '=', False),
        ('forecasted_start_date', '>=', dt_start),
    ]


def get_period_date_range(period):
    date_range = (None, None)
    date_now = datetime.today().date()

    if period == DashboardActivityFilterTimePeriod.today:
        date_range = (date_now, date_now)
    elif period == DashboardActivityFilterTimePeriod.this_week:
        date_range = get_date_range_in_week(date_now)
    elif period == DashboardActivityFilterTimePeriod.next_week:
        date_range = get_date_range_in_week(date_now + timedelta(7))

    return date_range


def get_period_datetime_range(date_start, date_end):
    dt_start = datetime.fromtimestamp(date_start).replace(hour=0, minute=0, second=0, microsecond=0)
    dt_end = datetime.fromtimestamp(date_end).replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt_start, dt_end



def get_dashboard_activity_filter_domain(status: DashboardActivityFilterStatus | None, date_start, date_end):
    dt_start, dt_end = get_period_datetime_range(date_start, date_end)
    filter_domain = []
    due_filter_domain = []
    overdue_filter_domain = []
    pending_filter_domain = [('date_deadline', '=', False)]

    if dt_start:
        due_filter_domain.append(('date_deadline', '>=', dt_start))
        overdue_filter_domain.append(('date_deadline', '<', dt_start))
    if dt_end:
        due_filter_domain.append(('date_deadline', '<=', dt_end))
        pending_filter_domain = expression.OR(
            [pending_filter_domain, [('date_deadline', '>', dt_end)]])

    if status == DashboardActivityFilterStatus.due_activities:
        filter_domain = due_filter_domain
    elif status == DashboardActivityFilterStatus.overdue:
        filter_domain = overdue_filter_domain
    elif status == DashboardActivityFilterStatus.pending:
        filter_domain = pending_filter_domain
    else:
        filter_domain = expression.OR(
            [due_filter_domain, overdue_filter_domain, pending_filter_domain])
    return filter_domain


def get_dashboard_activities_domain(current_user, query: str = None, filter_kwargs: dict = {}):
    """
    Returns the domain to use in the web_search_read function when gets activities of current_user.
    """
    domain = _get_dashboard_activities_domain(current_user)
    # search
    if query:
        domain.append(('name', 'ilike', query))

    # filter
    status = filter_kwargs.get('status')
    date_start = filter_kwargs.get('date_start')
    date_end = filter_kwargs.get('date_end')
    if not date_start or not date_end:
        return domain
    filter_domain = get_dashboard_activity_filter_domain(status, date_start, date_end)
    if filter_domain:
        domain = expression.AND([domain, filter_domain])
    return domain
