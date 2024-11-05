from odoo.addons.haverton_base_fastapi.schemas import (
    BaseModel,
    HavertonAddress,
    HavertonCompliance,
    HavertonRegion,
    HavertonServiceType,
    HavertonWrPreference,
)

# Properties to return via API


class ClientBase(BaseModel):
    uuid: str = None
    name: str | bool = None
    preferred_name: str | bool = None


class ClientContact(BaseModel):
    name: str | bool = None
    function: str | bool = None
    personal_mobile: str | bool = None
    personal_email: str | bool = None
    avatar_256: str | bool = False
    is_primary: bool = False


class Client(ClientBase):
    entity_code: str | bool = None
    phone: str | bool = None
    mobile: str | bool = None
    region_ids: list[HavertonRegion] | bool = None
    abn: str | bool = None
    url: str | bool = None
    wr_preference_id: HavertonWrPreference | bool = None
    child_ids: list[ClientContact] | bool = None
    address_id: HavertonAddress | bool = None
    service_type_ids: list[HavertonServiceType] | bool = None
    active: bool = None
    compliance_id: HavertonCompliance | bool = None
    avatar_256: str | bool = False
