from datetime import datetime
from enum import Enum

from odoo.addons.haverton_base_fastapi.schemas import (
    BaseModel,
    HavertonAddress,
    HavertonServiceType,
)

from .defect import DefectJob
from .variations import JobVariationApproval, JobVariationReason


class TodoType(str, Enum):
    activity = 'activity'
    defect = 'defect'
    variation = 'variation'


class TodoScreenType(str, Enum):
    todo_activities = 'todo_activities'
    todo_defects = 'todo_defects'
    todo_variations = 'todo_variations'


class TodoFilterCategoryCode(Enum):
    users = 'users'
    contract_no = 'contract_no'
    service_type = 'service_type'


class CountToDoList(BaseModel):
    total_activities: int | bool = None
    total_defects: int | bool = None
    total_variants: int | bool = None


class ToDoList(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    status: str | bool = None
    booked_start_date: datetime | bool = None
    forecasted_start_date: datetime | bool = None
    date_deadline: datetime | bool = None
    service_type: HavertonServiceType | bool = None
    approval_id: JobVariationApproval | bool = None
    reason_id: JobVariationReason | bool = None
    project_id: DefectJob | bool = None
    is_active_workflow: bool = None
    date_end: datetime | bool = None  # completion date
    address_id: HavertonAddress | bool = None
    booking_status: str | bool = None


class TodoFilterCategory(BaseModel):
    code: str | bool = None
    name: str | bool = None
