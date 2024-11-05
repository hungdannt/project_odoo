from odoo.addons.base_fastapi.schemas import PagedCollection
from odoo.addons.haverton_base_fastapi.schemas import (
    Attachment,
    MessageAuthor,
    MessageSubtype,
)
from odoo.http import request

from ..schemas import JobMessageBase


def get_messages(res_id: int, limit: int, offset: int, type: str = None):
    domain = [('res_id', '=', res_id), ('is_companion_message', '=', True)]
    if type:
        domain.append(('type', '=', type))
    specification = dict(JobMessageBase())
    specification['author_id'] = {'fields': dict(MessageAuthor())}
    specification['subtype_id'] = {'fields': dict(MessageSubtype())}
    specification['attachment_ids'] = {'fields': dict(Attachment())}
    res = request.env['mail.message'].sudo().web_search_read(
        domain=domain,
        specification=specification,
        limit=limit,
        offset=offset,
        order='date desc'
    )
    count = request.env['mail.message'].sudo().search_count(domain=domain)
    return PagedCollection[JobMessageBase](
        count=count,
        items=res['records']
    )
