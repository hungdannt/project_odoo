import base64
from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, File, UploadFile
from odoo import Command, _
from odoo.addons.base.models.res_users import Users
from odoo.addons.haverton_base_fastapi.dependencies import authorize_session
from odoo.http import request

from ..schemas import Attachment

router = APIRouter()


@router.post("/", response_model=List[Attachment])
def upload_attachment(current_user: Annotated[Users | None, Depends(authorize_session)],
                      record_uuid: Annotated[str, Body()] = None,
                      res_model_name: Annotated[str, Body()] = None,
                      field_name: Annotated[str, Body()] = None,
                      attach_files: List[UploadFile] = File(...)):
    """
    Upload attachments
    Params:
    When in the creation, only the attach_files parameter needs to be provided.
    - str record_uuid: The UUID of the object to which the attachment will be uploaded. (Example: The UUID of a user_input_line_ids in an inspection)
    - str res_model_name: The Odoo model to which this attachment is related. (Example: The model name of an answer user_input_line_ids is 'survey.user_input.line')
    - str field_name: The field name of the relation in the Odoo model. (Example: The field name of an answer user_input_line_ids is 'attach_images')
    return: uuid of attachments dan base64 data
    """
    record = False
    if record_uuid and res_model_name and field_name:
        record = request.env[res_model_name].validate_by_uuid(record_uuid)
    attachment_vals = [
        {
            'name': file.filename,
            'datas': base64.b64encode(file.file.read()),
            'public': True,
            'type': 'binary',
            'res_model': res_model_name or False,
            'res_id': record.id if record else False
        }
        for file in attach_files
    ]
    if attachment_vals:
        attachments = request.env['ir.attachment'].create(attachment_vals)
        if attachments:
            if record:
                record.write({field_name: [Command.link(aid) for aid in attachments.ids]})
            return attachments


@router.delete("/{uuid}")
def delete_attachments(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Delete a attachment
    """
    attachment = request.env['ir.attachment'].validate_by_uuid(uuid)
    attachment.unlink()
    return {'detail': _('File deleted successfully')}
