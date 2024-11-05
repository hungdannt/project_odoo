from odoo import Command, models
from odoo.http import request

from ..schemas import MessageCreate


def prepare_haverton_message_vals(
    payload: MessageCreate,
    res_object: models.Model = None,
    subtype_code: str = None,
):
    vals = {
        **payload.model_dump(),
        'is_companion_message': True,
        'author_id': request.env.user.partner_id.id,
    }
    if subtype_code:
        subtype = request.env['mail.message.subtype'].browse_by_haverton_code(
            subtype_code)
        if subtype:
            vals['subtype_id'] = subtype.id
    # extract attachments
    attachment_uuids = vals.pop('attachment_uuids', None)
    if attachment_uuids:
        attachments = request.env['ir.attachment'].browse_by_uuids(
            attachment_uuids)
        if attachments:
            vals['attachment_ids'] = [Command.set(attachments.ids)]
    # extract users
    user_uuids = vals.pop('user_uuids', None)
    if user_uuids:
        users = request.env['res.users'].browse_by_uuids(
            user_uuids)
        if users:
            vals['user_ids'] = [Command.set(users.ids)]
    if res_object:
        vals['model'] = res_object._name
        vals['res_id'] = res_object.id
    return vals


def add_new_message(
    payload: MessageCreate,
    res_object: models.Model = None,
    subtype_code: str = None,
):
    vals = prepare_haverton_message_vals(payload, res_object, subtype_code)
    return request.env['mail.message'].sudo().create(vals)
