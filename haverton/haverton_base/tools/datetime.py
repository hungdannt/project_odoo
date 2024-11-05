from datetime import date, datetime, timedelta

from odoo.http import request
from odoo.tools.misc import get_lang


def convert_date_to_user_lang_format(date_obj: date):
    user_lang = get_lang(request.env)
    if not user_lang or not isinstance(date_obj, date):
        return date_obj
    return date_obj.strftime(user_lang.date_format)


def convert_datetime_to_user_lang_format(datetime_obj: datetime):
    user_lang = get_lang(request.env)
    if not user_lang:
        return datetime_obj
    date_format = user_lang.date_format
    time_format = user_lang.time_format
    return datetime_obj.strftime(f"{date_format} {time_format}")


def get_date_range_in_week(date_now):
    _, _, weekday = date_now.isocalendar()
    date_this_week_start = date_now - timedelta(weekday - 1)
    date_this_week_end = date_this_week_start + timedelta(6)
    return (date_this_week_start, date_this_week_end)


def get_domain_filter_datetime_in_day(date: date, field_name: str):
    dt_start = datetime.combine(date, datetime.min.time())
    dt_end = datetime.combine(date, datetime.max.time())
    return [(field_name, '>=', dt_start), (field_name, '<=', dt_end)]
