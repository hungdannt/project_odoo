from datetime import datetime
from enum import Enum
from typing import List

from odoo.addons.haverton_base_fastapi.schemas import (
    BaseModel,
    Currency,
    HavertonAddress,
    HavertonCompliance,
    HavertonLocation,
    HavertonRegion,
    HavertonServiceType,
    MessageBase,
    MessageCreate,
)
from odoo.addons.haverton_base_fastapi.utils import common as utils
from odoo.addons.haverton_service_provider.schemas import ClientBase
from odoo.exceptions import UserError
from odoo.http import request
from pydantic import Field

from ..schemas import DefectMessage


class DashboardActivityProject(BaseModel):
    uuid: str | bool = None


class DashboardActivity(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    contract_no: str | bool = None
    dashboard_activity_status: str | bool = None
    project_id: DashboardActivityProject | bool = None
    address_id: HavertonAddress | bool = None


class JobMasterDataField(str, Enum):
    user = 'user'
    workflow_status = 'workflow_status'


class DashboardActivityFilterStatus(str, Enum):
    pending = 'pending'
    due_activities = 'due_activities'
    overdue = 'overdue'


class DashboardActivityFilterTimePeriod(str, Enum):
    today = 'today'
    this_week = 'this_week'
    next_week = 'next_week'


class DashboardActivityFilterCategory(str, Enum):
    status = 'status'
    time_period = 'time_period'


class JobFilterStatus(str, Enum):
    completed = 'completed'
    incompleted = 'incompleted'


class JobFilterJobStatusGroup(str, Enum):
    any_workflows = 'any_workflows'
    active_workflows = 'active_workflows'
    inactive_workflows = 'inactive_workflows'


class JobSearch(str, Enum):
    contract_no = 'contract_no'
    address = 'address'


class JobSortBy(str, Enum):
    contract_no = 'contract_no'
    address = 'address'
    haverton_write_date = 'haverton_write_date'
    write_user_name = 'write_user_name'


class JobActivityFilterStatus(str, Enum):
    normal = 'normal'
    overdue = 'overdue'
    completed = 'completed'


# Properties to return via API

class JobActivityBase(BaseModel):
    uuid: str = None
    name: str | bool = None
    booking_status: str | bool = None
    status: str | bool = None
    date_end: datetime | bool = None  # completion date
    booked_start_date: datetime | bool = None


class JobStatus(BaseModel):
    name: str | bool = None
    is_active_workflow: bool = None


class JobActivityUser(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class JobSupervisorUser(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class JobActivityServiceProvider(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    preferred_name: str | bool = None


class JobActivityQuestionInspection(BaseModel):
    uuid: str | bool = None
    submit_datetime: datetime | bool = None
    name: str | bool = None
    state: str | bool = None


class JobActivityQuestion(BaseModel):
    uuid: str | bool = None
    sequence: int | bool = None
    question: str | bool = None
    is_inspection_question: bool = None


class JobActivityQuestionAnswerBase(BaseModel):
    uuid: str | bool = None
    is_completed: bool = None
    is_not_applicable: bool = None


class JobActivityQuestionAnswer(JobActivityQuestionAnswerBase):
    question_id: JobActivityQuestion | bool = None
    inspection_id: JobActivityQuestionInspection | bool = None

    def from_instance(self, instance):
        question = instance.question_id
        self.uuid = instance.uuid
        self.is_completed = instance.is_completed
        self.is_not_applicable = instance.is_not_applicable
        self.question_id = utils.get_serializer(
            question, JobActivityQuestion)
        self.inspection_id = False
        if question and question.is_inspection_question:
            try:
                survey = question.get_survey()
                inspection_id = request.env['survey.user_input'].get_inspection(
                    survey, instance.task_id)
                self.inspection_id = utils.get_serializer(
                    inspection_id, JobActivityQuestionInspection)
            except UserError:
                pass


class JobActivityComplete(BaseModel):
    uuid: str = None
    name: str | bool = None
    user_id: JobActivityUser | bool = None
    date_end: datetime | bool = None
    sequence: int | bool = None
    haverton_activity_question_answer_ids: List[JobActivityQuestionAnswer] | bool = None
    contract_no: str | bool = None
    service_type: HavertonServiceType | bool = None
    job_uuid: str | bool = None

    def from_instance(self, instance):
        self.uuid = instance.uuid
        self.name = instance.name
        self.user_id = utils.get_serializer(
            instance.user_id, JobActivityUser)
        self.date_end = instance.date_end
        self.sequence = instance.sequence
        self.contract_no = instance.contract_no
        self.job_uuid = instance.project_id.uuid if instance.project_id else None
        self.service_type = utils.get_serializer(
            instance.service_type, HavertonServiceType)

        question_answer_ids = []
        for i in instance.haverton_activity_question_answer_ids:
            answer = JobActivityQuestionAnswer()
            answer.from_instance(i)
            question_answer_ids.append(answer)
        self.haverton_activity_question_answer_ids = question_answer_ids


class JobActivity(JobActivityBase):
    sequence: int | bool = None
    total_defects: int = None
    forecasted_start_date: datetime | bool = None
    start_date: datetime | bool = None
    date_deadline: datetime | bool = None
    days_until_completion: int | bool = Field(default=None, deprecated=True)
    days_remaining: int | bool = Field(default=None, deprecated=True)
    comp: HavertonCompliance | bool = None
    sequence_predecessors: list | bool = None
    sequence_successors: list | bool = None
    user_id: JobActivityUser | bool = None
    job_status: str | bool = None
    is_active_workflow: bool = Field(default=None, deprecated=True)
    service_type: HavertonServiceType | bool = None
    service_provider_id: JobActivityServiceProvider | bool = False
    inspection_status: str | bool = False
    last_message: DefectMessage | bool = Field(default=None, deprecated=True)
    contract_no: str | bool = None
    job_address: str | bool = None
    booking_status: str | bool = Field(default=None, deprecated=True)
    status: str | bool = Field(default=None, deprecated=True)

    @property
    def fields_hidden(self):
        return self.get_fields_hidden_by_field_name('project.task', 'show_on_mobile_activity_detail')

    @property
    def fields_required(self):
        return ['booked_start_date', 'forecasted_start_date', 'date_end', 'uuid', 'user_id']


class JobBase(BaseModel):
    uuid: str = None
    address: str | bool = None
    client_name: str | bool = None
    client_id: ClientBase | bool = None
    contract_no: str | bool = None
    overdue: int = None
    stage_id: JobStatus | bool = None
    is_completed_by_user: bool = None


class Job(JobBase):
    address: str | bool = Field(default=None, deprecated=True)
    address_details: str | bool = None
    date_start: datetime | bool = None
    date: datetime | bool = Field(default=None, deprecated=True)
    contract_start_on: datetime | bool = None
    contract_end_on: datetime | bool = None
    contract_house_design: str | bool = None
    region_id: HavertonRegion | bool = None
    location_ids: list[HavertonLocation] | bool = None
    currency_id: Currency | bool = Field(default=None, deprecated=True)
    contract_value_ex_gst: float = None
    contract_value_inc_gst: float = None
    contract_details: str | bool = Field(default=None, deprecated=True)
    client_name: str | bool = Field(default=None, deprecated=True)
    client_id: ClientBase | bool = Field(default=None, deprecated=True)
    overdue: int = Field(default=None, deprecated=True)
    is_completed_by_user: bool = Field(default=None, deprecated=True)
    supervisor_id: JobSupervisorUser | bool = Field(
        default=None, deprecated=True)
    last_message: DefectMessage | bool = Field(default=None, deprecated=True)

    @property
    def fields_hidden(self):
        return self.get_fields_hidden_by_field_name('project.project', 'show_on_mobile_job_detail')

    @property
    def fields_required(self):
        return ['is_completed_by_user', 'uuid', 'contract_start_on', 'contract_end_on']


class JobMessageSubtypeCode(str, Enum):
    note = 'note'
    booking = 'booking'


class JobMessageBase(MessageBase):
    task_booked_start_date: datetime | bool = None


class JobActivityBookingMessageCreate(MessageCreate):
    task_booked_start_date: datetime | bool
