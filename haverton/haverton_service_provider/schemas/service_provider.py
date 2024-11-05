from enum import Enum

from odoo.addons.haverton_base_fastapi.schemas import (
    BaseModel,
    HavertonCompliance,
    HavertonRegion,
    HavertonServiceType,
    HavertonWrPreference,
)
from pydantic import Field


class ServiceProviderMasterData(str, Enum):
    contract_no = 'contract_no'
    region = 'region'
    service_type = 'service_type'
    compliance = 'compliance'
    work_category = 'work_category'


class ServiceProviderSearch(str, Enum):
    name = 'name'
    service_type = 'service_type'


class ServiceProviderSortBy(str, Enum):
    name = 'name'
    preferred_name = 'preferred_name'
    contract = 'contract'
    region = 'region'
    service_type = 'service_type'
    compliance = 'compliance'
    work_category = 'work_category'


# Properties to return via API
class ServiceProviderBase(BaseModel):
    uuid: str = None
    name: str | bool = None
    preferred_name: str | bool = None
    service_type_ids: list[HavertonServiceType] | bool = None
    active: bool = None
    compliance_id: HavertonCompliance | bool = None
    avatar_256: str | bool = False


class ServiceProviderContact(BaseModel):
    name: str | bool = None
    function: str | bool = None
    phone: str | bool = None
    mobile: str | bool = None
    email: str | bool = None
    avatar_256: str | bool = False
    is_primary: bool = False


class ServiceProvider(ServiceProviderBase):
    entity_code: str | bool = None
    phone: str | bool = None
    mobile: str | bool = Field(default=None, deprecated=True)
    region_ids: list[HavertonRegion] | bool = None
    abn: str | bool = None
    url: str | bool = None
    wr_preference_id: HavertonWrPreference | bool = None
    child_ids: list[ServiceProviderContact] | bool = None
    formatted_address: str | bool = None
    avatar_256: str | bool = Field(default=None, deprecated=True)
    active: bool = Field(default=None, deprecated=True)

    @property
    def fields_hidden(self):
        return self.get_fields_hidden_by_field_name('res.partner', 'show_on_mobile_service_provider_detail')

    @property
    def fields_required(self):
        return ['preferred_name', 'uuid']
