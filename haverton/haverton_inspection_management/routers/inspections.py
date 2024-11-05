from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from odoo import Command, _, fields
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import (
    authorize_session,
    format_query,
)
from odoo.addons.haverton_base_fastapi.utils import common as utils
from odoo.addons.haverton_job_management.utils import defect as defect_utils
from odoo.http import request

from ..schemas import (
    Inspection,
    InspectionCreatePayload,
    InspectionMasterData,
    InspectionMasterDataSearch,
    InspectionPayload,
    InspectionQuestionPayload,
)
from ..utils import inspection as inspection_utils

router = APIRouter()


@router.get("/masterdata", response_model=PagedCollection[dict])
def get_inspection_masterdata(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        master_field: InspectionMasterData,
        search_field: InspectionMasterDataSearch,
        q: Annotated[str, Depends(format_query)] = None,
        job_uuid: str = None,
        survey_uuid: str = None,
):
    """
    Get master data for the inspection creating screen.
    Params:
    - master_field: name of inspection master data field
    - search_field: name of field needed to search
     + search_field = "address" or "contract_no" if master_field == "project_id"
     + search_field = "name" if master_field == "task_id"
     + search_field = "title" if master_field == "survey_id"
    """
    model_name = request.env['survey.user_input'][master_field.value]._name
    domain = [(search_field.value, 'ilike', q)] if q else []
    if master_field == InspectionMasterData.survey_id:
        domain.extend([('is_clone', '=', False), ('state', '=', 'published')])
    if master_field == InspectionMasterData.task_id:
        domain.extend([('haverton_task_type', '=', 'activity'),
                      ('date_end', '=', False)])
        if survey_uuid:
            task_inspections = request.env['survey.user_input'].sudo().search(
                [('parent_survey_id.uuid', '=', survey_uuid)])
            if task_inspections:
                domain.append(
                    ('id', 'not in', task_inspections.mapped('task_id').ids))
        if job_uuid:
            domain.append(('project_id.uuid', '=', job_uuid))
    response_field = inspection_utils.get_inspection_masterdata_response_field(
        master_field)
    record, total = utils.get_masterdata(
        model_name, response_field, paging.limit, paging.offset, domain)
    return PagedCollection[dict](
        count=total,
        items=record
    )


@router.get("/{uuid}", response_model=Inspection)
def get_inspection(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the inspections detail
    """
    inspection = request.env['survey.user_input'].sudo().validate_by_uuid(uuid)
    inspection_data = inspection.sudo().prepare_haverton_data()

    return Inspection(**inspection_data)


@router.delete("/{uuid}/defects/{defect_uuid}")
def delete_defect(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str, defect_uuid: str):
    """
    Remove the defect from the inspection
    """
    inspection = request.env['survey.user_input'].sudo().validate_by_uuid(uuid)
    defect = defect_utils.validate_defect_uuid(defect_uuid)
    defect = inspection.write({
        'defect_ids': [Command.unlink(defect.id)]
    })
    return {'detail': _('Successfully remove the defect from the inspection.')}


@router.put("/{uuid}", response_model=Inspection)
def update_inspection(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        uuid: str,
        updated_inspection_data: InspectionPayload = None,
        questions: List[InspectionQuestionPayload] = None):
    """
    Update Inspection API:
    - str uuid: uuid of inspection
    - str state: Represents the current state of the inspection. It transitions to
    'in_progress' after initiation and remains so until marked as 'done' upon submission.
    - list InspectionQuestionPayload questions: A list containing details of each question and its answer.
    """
    inspection = request.env['survey.user_input'].validate_by_uuid(uuid)
    if questions:
        inspection.sudo().update_inspection_answer(questions)
    if updated_inspection_data:
        updated_data = updated_inspection_data.model_dump()
        updated_data = request.env['survey.user_input'].prepare_haverton_values(
            updated_data, is_update=True)
        if updated_data.get('state') == 'done':
            updated_data['submit_datetime'] = fields.Datetime.now()
            updated_data['sign_datetime'] = fields.Datetime.now()
        inspection.sudo().web_save(updated_data, specification={})
    inspection_data = inspection.sudo().prepare_haverton_data()
    return Inspection(**inspection_data)


@router.post("/", response_model=Inspection)
def create_inspection(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        inspection_payload: InspectionCreatePayload):
    """
    API for Create Inspection
    """
    survey, project, task = inspection_utils.validate_inspection_creation_payload(
        inspection_payload)
    inspection_vals = request.env['survey.user_input'].prepare_inspection_creation_vals(
        survey, project, task)
    return request.env['survey.user_input'].create(inspection_vals)


@router.post("/survey_masterdata")
def generate_survey_masterdata(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        file_path: str = None):
    """
    API for Generate the masterdata of Surveys.
    If not file_path, data will be not saved in server.
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    content = """
<?xml version="1.0" ?>
<odoo>
    <data noupdate="1">
    """
    s_records = inspection_utils.prepare_survey_records()
    content += s_records
    content += """
    </data>
</odoo>
"""
    if file_path:
        f = open(file_path, "w+")
        f.write(content)
        f.close()
    return Response(content=content, media_type="application/xml")


@router.post("/question_template_masterdata")
def generate_question_template_masterdata(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        file_path: str = None):
    """
    API for Generate the masterdata of Question Templates.
    If not file_path, data will be not saved in server.
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    content = """
<?xml version="1.0" ?>
<odoo>
    <data noupdate="1">
    """
    s_records = inspection_utils.prepare_question_template_records()
    content += s_records
    content += """
    </data>
</odoo>
"""
    if file_path:
        f = open(file_path, "w+")
        f.write(content)
        f.close()
    return Response(content=content, media_type="application/xml")
