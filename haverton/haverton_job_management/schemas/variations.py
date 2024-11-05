from datetime import datetime
from enum import Enum

from odoo.addons.haverton_base_fastapi.schemas import BaseModel, HavertonServiceType


class VariationMasterData(str, Enum):
    approval_id = 'approval_id'


class JobVariationApproval(BaseModel):
    name: str | bool = None


class JobVariationReason(BaseModel):
    name: str | bool = None


class JobVariationActivity(BaseModel):
    uuid: str = None
    name: str | bool = None
    service_type: HavertonServiceType | bool = None
    forecasted_start_date: datetime | bool = None


class JobVariationBase(BaseModel):
    uuid: str = None
    name: str | bool = None
    approval_id: JobVariationApproval | bool = None
    reason_id: JobVariationReason | bool = None


class VariationUser(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class VariationServiceProvider(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    preferred_name: str | bool = None


class VariationDocument(BaseModel):
    uuid: str | bool = None
    description: str | bool = None
    haverton_document_type: str | bool = None
    attach_on: datetime | bool = None
    haverton_created_by: VariationUser | bool = None
    is_sent_to_client: bool = None
    is_sent_to_service_provider: bool = None
    is_available_offline: bool = None


class JobVariation(JobVariationBase):
    sequence: int | bool = None
    reference: str | bool = None
    start_date: datetime | bool = None
    invoice_number: str | bool = None
    approval_last_updated_by: str | bool = None
    create_by: str | bool = None

    @property
    def fields_hidden(self):
        return self.get_fields_hidden_by_field_name('project.task', 'show_on_mobile_variation_detail')

    @property
    def fields_required(self):
        return ['uuid']
