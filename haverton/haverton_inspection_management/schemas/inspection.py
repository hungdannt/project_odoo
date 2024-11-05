from datetime import datetime
from enum import Enum
from typing import List

from odoo.addons.haverton_base_fastapi.schemas import (
    Attachment,
    AttachmentURL,
    BaseModel,
)
from odoo.addons.haverton_job_management.schemas import DefectBase, DefectJob
from pydantic import Field


class InspectionStatus(str, Enum):
    new = 'new'
    in_progress = 'in_progress'
    done = 'done'


class InspectionMasterData(str, Enum):
    survey_id = 'survey_id'
    project_id = 'project_id'
    task_id = 'task_id'


class InspectionMasterDataSearch(str, Enum):
    address = 'address'  # Job
    contract_no = 'contract_no'  # Job
    name = 'name'  # JobActivity
    title = 'title'  # Survey


class InspectionQuestionAnswer(BaseModel):
    uuid: str | bool = None
    value: str | bool = None


class InspectionQuestionBase(BaseModel):
    uuid: str | bool = None


class InspectionSupervisorUser(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class InspectionAnswerLine(BaseModel):
    selected_options: List[InspectionQuestionAnswer] | bool = None
    attachment_ids: List[AttachmentURL] | bool = None
    value_text_box: str | bool = None
    value_char_box: str | bool = None
    value_numerical_box: float | bool = None
    value_date: datetime | bool = None
    value_datetime: datetime | bool = None
    location: dict | bool = None
    user_signature: str | bool = None
    user_signature_raw: str | bool = None
    user_id: InspectionSupervisorUser | bool = None
    is_clicked: bool = Field(default=None, title="Is user clicked on the question?")


class InspectionContition(BaseModel):
    question_uuid: str
    values: list | bool = None
    operator: str | bool = None


class InspectionRule(BaseModel):
    visible_conditions: List[InspectionContition] | bool = None


class InspectionQuestion(InspectionQuestionBase):
    title: str | bool = None
    haverton_question_type: str | bool = None
    view_in_map: bool = None
    autofill_user: bool = None
    label_for_user_id: str | bool = None
    autofill_datetime: bool = None
    autofill_location: bool = None
    constr_mandatory: bool = None
    suggested_answer_ids: List[InspectionQuestionAnswer] | bool = None
    inspection_rules: InspectionRule | bool = None
    answers: InspectionAnswerLine | bool = None
    constr_error_msg: str | bool = None
    autofill: bool = None
    autofill_field: str | bool = None
    text_before_click: str | bool = None
    text_after_click: str | bool = None


class InspectionSection(BaseModel):
    uuid: str | bool = None
    title: str | bool = None
    questions: List[InspectionQuestion] | bool = None


class InspectionBase(BaseModel):
    uuid: str = None
    name: str | bool = None
    activity_name: str | bool = None
    address: str | bool = None
    job_address: str | bool = None
    deadline: datetime | bool = None
    overdue: bool = None
    state: str | bool = None
    contract_no: str | bool = None


class InspectionTemplate(BaseModel):
    uuid: str | bool = None
    question_and_page_ids: List[InspectionQuestion]


class Inspection(InspectionBase):
    sequence: int | bool = None
    user_signature: str | bool = None
    user_signature_raw: str | bool = None
    aggregate_location_image: Attachment | bool = None
    house_design: str | bool = None
    project_id: DefectJob | bool = None
    user_id: InspectionSupervisorUser | bool = None
    sign_datetime: datetime | bool = None
    sections: List[InspectionSection] | bool = None
    defect_ids: List[DefectBase] | bool = None


class InspectionLinePayload(BaseModel):
    selected_options: List[str] | bool = None
    attachment_uuids: List[str] | bool = None
    attach_map_image:  str | bool = None
    value_text_box: str | bool = None
    value_char_box: str | bool = None
    value_numerical_box: float | bool = None
    value_date: datetime | bool = None
    value_datetime: datetime | bool = None
    location: dict | bool = None
    user_uuid:  str | bool = None
    user_signature: str | bool = None
    user_signature_raw: str | bool = None
    is_clicked: bool = Field(default=None, title="Is user clicked on the question?")


class InspectionQuestionPayload(BaseModel):
    uuid: str
    visible: bool = None
    answers: InspectionLinePayload | bool = None


class InspectionCreatePayload(BaseModel):
    service_question_uuid: str | bool = Field(
        default=None, title="The service question UUID.")
    survey_uuid: str | bool = Field(
        default=None, title="The original survey UUID.")
    project_uuid: str | bool = Field(
        default=None, title="The job UUID.")
    task_uuid: str | bool = Field(
        default=None, title="The activity UUID.")


class InspectionPayload(BaseModel):
    state: InspectionStatus | bool = None
    user_signature: str | bool = None
    user_signature_raw: str | bool = None
    sign_datetime: datetime | bool = None
    aggregate_location_image: str | bool = None
