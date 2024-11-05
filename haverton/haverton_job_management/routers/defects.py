from typing import Annotated, List

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
)
from odoo.addons.haverton_base_fastapi.utils import message as base_message_utils
from odoo.exceptions import UserError
from odoo.http import request

from ..schemas import (
    Defect,
    DefectAttachmentSectionCreate,
    DefectMasterData,
    DefectPayload,
    JobMessageBase,
    JobMessageSubtypeCode,
)
from ..utils import defect as defect_utils
from ..utils import master_data as master_data_utils
from ..utils import message as message_utils

router = APIRouter()


@router.get("/masterdata", response_model=PagedCollection[dict])
def get_defect_masterdata(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        master_field: DefectMasterData,
        q: Annotated[str, Depends(format_query)] = None,
):
    """
    Get master data for defects based on the specified field name.
    Params:
    - DefectMasterData master_field: name of defect master data field
    """
    field_name = master_data_utils.get_masterdata_field_name(master_field)
    model_name = request.env['project.task'][master_field.value]._name
    domain = [(field_name, 'ilike', q)]
    if master_field == DefectMasterData.service_provider_id:
        domain.extend([('haverton_contact_type', '=', 'service_provider'), ('active', '=', True)])
    if master_field == DefectMasterData.haverton_defect_category_id:
        domain.append(('active', '=', True))
    record, total = master_data_utils.get_masterdata(
        model_name, field_name, paging.limit, paging.offset, domain)
    return PagedCollection[dict](
        count=total,
        items=record
    )


@router.get("/{uuid}", response_model=Defect)
def get_defect(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the defect detail
    """
    defect = defect_utils.validate_defect_uuid(uuid)
    return defect


@router.delete("/{uuid}")
def delete_defect(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Delete a defect
    """
    defect = defect_utils.validate_defect_uuid(uuid)
    defect.sudo().unlink()
    return {'detail': _('Defect deleted successfully')}


@router.post("/", response_model=Defect)
def create_defect(current_user: Annotated[Users | None, Depends(authorize_session)],
                  defect_data: DefectPayload,
                  images_section: List[DefectAttachmentSectionCreate] | bool = None):
    """
    Create a defect.
    Params defect_data: The data to create the defect.:
    - datetime forecasted_start_date, date_deadline, booked_start_date: datetime in ISO 8601 format with UTC timezone.
    - int sequence.
    - str name.
    - str service_type: uuid of Service Type.
    - str user_id: uuid of User.
    - str location_ids: list of the Location uuid.
    - str haverton_defect_category_id: uuid of defect category.
    - int work_day_duration.
    - str defect_details.
    - str defect_action.
    - float defect_amount.
    - bool is_back_charge.
    - str service_provider_id: uuid of Service Provider.
    - str project_id: uuid of Job.
    - bool is_auto_assign_service_provider.
    - str contract_no.
    - str job_activity_id: uuid of activity link with this defect.
    """
    defect_data = defect_data.model_dump()
    if not defect_data:
        raise UserError(_('No data provided.'))
    defect_value = request.env['project.task'].sudo(
    ).prepare_haverton_values(defect_data)
    defect_value['haverton_task_type'] = 'defect'
    defect_value['user_id'] = current_user.id
    if defect_value.get('is_auto_assign_service_provider', False):
        job = request.env['project.project'].sudo(
        ).validate_by_uuid(defect_data['project_id'])
        defect_value['service_provider_id'] = job.get_service_provider(
            defect_data['service_type'])
    defect = request.env['project.task'].sudo().create(defect_value)
    if images_section and defect:
        defect.sudo().create_attachment_section(images_section)
    defect.is_send_mail_create_defect = True
    return defect


@router.post("/{uuid}/uncomplete", response_model=Defect)
def uncomplete_defect(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    """
    Uncomplete a defect.
    Params:
    - str uuid: The UUID of the defect to be uncompleted.
    """
    defect = defect_utils.validate_defect_uuid(uuid)
    defect.date_end = None
    return defect


@router.put("/{uuid}", response_model=Defect)
def update_defect(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        uuid: str,
        updated_defect_data: DefectPayload | bool = None,
        images_section: List[DefectAttachmentSectionCreate] | bool = None):
    """
    Update a defect.
    Params:
    - str uuid: The UUID of the defect to be updated.
    - images_section: ist of image section values including UUID (optional), description, and list of image UUIDs
    """

    defect = defect_utils.validate_defect_uuid(uuid)
    defect_vals = {}
    if updated_defect_data:
        defect_vals = updated_defect_data.model_dump()
        defect_vals = request.env['project.task'].prepare_haverton_values(defect_vals, is_update=True)
    if (defect_vals.get('is_auto_assign_service_provider', False) and not defect.is_auto_assign_service_provider) or (
            defect_vals.get('is_auto_assign_service_provider', False) and defect.service_type.uuid != defect_vals.get(
            'service_type')):
        defect_vals['service_provider_id'] = defect.project_id.get_service_provider(updated_defect_data.service_type)
    if defect_vals:
        defect.sudo().web_save(defect_vals, specification={})
    if not images_section and defect.images_section:
        defect.images_section.sudo().unlink()
    if images_section:
        defect.sudo().create_attachment_section(images_section, is_update=True)
    return defect


@router.get("/{uuid}/messages", response_model=PagedCollection[JobMessageBase])
def get_defect_messages(
    paging: Annotated[Paging, Depends(paging)],
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    defect = defect_utils.validate_defect_uuid(uuid)
    return message_utils.get_messages(defect.id, paging.limit, paging.offset)


@router.post("/{uuid}/messages", response_model=Message)
def add_new_defect_message(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str,
    payload: MessageCreateWithAttachment,
):
    defect = defect_utils.validate_defect_uuid(uuid)
    return base_message_utils.add_new_message(payload, res_object=defect, subtype_code=JobMessageSubtypeCode.note)
