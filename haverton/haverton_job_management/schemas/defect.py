from datetime import datetime
from enum import Enum
from typing import List

from odoo.addons.haverton_base_fastapi.schemas import (
    BaseModel,
    Currency,
    HavertonDefectCategory,
    HavertonLocation,
    HavertonServiceType,
)
from pydantic import Field


class DefectBase(BaseModel):
    uuid: str = None
    name: str | bool = None
    status: str | bool = None
    defect_description: str | bool = None
    forecasted_start_date: datetime | bool = None
    date_deadline: datetime | bool = None


class DefectServiceProvider(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    preferred_name: str | bool = None


class DefectJob(BaseModel):
    uuid: str | bool = None
    contract_no: str | bool = None
    is_completed_by_user: bool = None


class DefectUser(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class DefectLocation(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class DefectMasterData(str, Enum):
    service_type = 'service_type'
    location_ids = 'location_ids'
    haverton_defect_category_id = 'haverton_defect_category_id'
    service_provider_id = 'service_provider_id'

    
class DefectAttachImage(BaseModel):
    uuid: str | bool = None
    datas: str | bool = None


class DefectAttachmentSection(BaseModel):
    uuid: str | bool = None
    description: str | bool = None
    attach_images: List[DefectAttachImage] | bool = None


class DefectAttachmentSectionCreate(BaseModel):
    uuid: str | bool = None
    description: str | bool = None
    attach_images: List[str] | bool = None


class DefectMessage(BaseModel):
    author_id: DefectUser | bool = None
    date: datetime | bool = None
    body: str | bool = None
    haverton_message_type: str | bool = None


class Defect(DefectBase):
    sequence: int | bool = None
    name: str | bool = Field(default=None, deprecated=True)
    create_date: datetime | bool = Field(default=None, deprecated=True)
    haverton_create_date: datetime | bool = None
    create_uid: DefectUser | bool = Field(default=None, deprecated=True)
    currency_id: Currency | bool = None
    service_type: HavertonServiceType | bool = Field(
        default=None, deprecated=True)
    defect_type_id: HavertonServiceType | bool = None
    booked_start_date: datetime | bool = None
    user_id: DefectUser | bool = None
    location_ids: list[HavertonLocation] | bool = None
    haverton_defect_category_id: HavertonDefectCategory | bool = None
    work_day_duration: int | bool = None
    defect_details: str | bool = None
    defect_action: str | bool = None
    defect_amount: float | bool = None
    is_back_charge: bool = None
    service_provider_id: DefectServiceProvider | bool = None
    project_id: DefectJob | bool = Field(default=None, deprecated=True)
    is_auto_assign_service_provider: bool = None
    charge_to: DefectServiceProvider | bool = None
    contract_no: str | bool = None
    images_section: List[DefectAttachmentSection] | bool = None
    last_message: DefectMessage | bool = Field(default=None, deprecated=True)
    create_by: str | bool = None
    date_end: datetime | bool = None

    @property
    def fields_hidden(self):
        return self.get_fields_hidden_by_field_name('project.task', 'show_on_mobile_defect_detail')

    @property
    def fields_required(self):
        return ['date_end', 'is_back_charge', 'status', 'date_deadline', 'booked_start_date', 'is_auto_assign_service_provider', 'contract_no', 'forecasted_start_date', 'uuid', 'currency_id']


class DefectPayload(BaseModel):
    forecasted_start_date: datetime | bool = Field(default=None, description="Forecasted Start Date")
    date_deadline: datetime | bool = Field(default=None, description="Forecasted Completion")
    sequence: int | bool = Field(default=None, description="Sequence")
    name: str | bool = Field(default=None, description="Description")
    service_type: str | bool = Field(default=None, description="Service Type")
    defect_type_id: str | bool = Field(default=None, description="Type")
    booked_start_date: datetime | bool = Field(default=None, description="Booked start")
    user_id: str | bool = Field(default=None, description="User")
    location_ids: list[str] | bool = Field(default=None, description="Location")
    haverton_defect_category_id: str | bool = Field(default=None, description="Defect Category")
    work_day_duration: int | bool = Field(default=None, description="Duration (in work days)")
    defect_description: str | bool = Field(default=None, description="Defect Description")
    defect_details: str | bool = Field(default=None, description="Detail")
    defect_action: str | bool = Field(default=None, description="Action")
    defect_amount: float | bool = Field(default=None, description="Amount")
    is_back_charge: bool = Field(default=None, description="Back Charge")
    service_provider_id: str | bool = Field(default=None, description="Service Provider")
    project_id: str | bool = Field(default=None, description="Job")
    is_auto_assign_service_provider: bool = Field(default=None, description="Auto-assign Service Provider")
    charge_to: str | bool = Field(default=None, description="Charge to")
    job_activity_id: str | bool = Field(default=None, description="Activity")
    inspection_id: str | bool = Field(default=None, description="Inspection")
    date_end: datetime | bool = Field(default=None, description="Completion Date")
