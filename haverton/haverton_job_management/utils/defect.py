from odoo import _
from odoo.exceptions import UserError
from odoo.http import request


def validate_defect_uuid(uuid: str):
    defect = request.env['project.task'].validate_by_uuid(uuid)
    if defect.haverton_task_type != 'defect':
        raise UserError(_('This is not a defect'))
    return defect


def paginate_and_filter_by_status(records, paging, status=None):
    if not records:
        return [], 0
    if status:
        records = [record for record in records if record.get('status') in status]
    count = len(records)
    paginated_records = records[paging.offset:paging.offset + paging.limit]
    return paginated_records, count
