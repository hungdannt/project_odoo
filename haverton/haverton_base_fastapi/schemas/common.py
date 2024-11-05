from datetime import datetime, timezone
from enum import Enum

from odoo.addons.haverton_base.models.res_users import EMAIL_CONSTRAIN
from odoo.http import request
from pydantic import BaseModel as PydanticBaseModel
from pydantic import constr

EmailConstraints = constr(pattern=EMAIL_CONSTRAIN)


class OrderBy(str, Enum):
    asc = 'ASC'
    desc = 'DESC'


class BaseModel(PydanticBaseModel):
    @property
    def fields_hidden(self):
        """
        Returns fields hidden in the response
        """
        return []

    @property
    def fields_required(self):
        """
        Returns fields required in response data of a model
        """
        return []

    def get_fields_hidden_by_field_name(self, odoo_model, visible_by: str):
        """
        Return fields hidden in the response by the visible_by field of the ir_model_fields model.
        Params:
            - odoo_model: The Odoo model name which this Pydantic model represents.
            - visible_by: The field name determines whether a field is shown or not.
        """
        try:
            return request.env['ir.model.fields'].sudo().search([
                (visible_by, '!=', None), (visible_by, '=', False), ('model', '=', odoo_model)]).mapped('name') or []
        except AttributeError:
            return []

    def model_post_init(self, *args, **kwargs):
        super().model_post_init(*args, **kwargs)
        for field_name in self.fields_hidden:
            self.__dict__.pop(field_name, None)

        for field in self:
            value = field[1]
            if isinstance(value, datetime):
                # convert naive datetime to aware datetime to show on mobile
                value = value.replace(tzinfo=timezone.utc)
                setattr(self, field[0], value)


# money
class Currency(BaseModel):
    name: str | bool = None
    symbol: str | bool = None


class HavertonCompliance(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    font_color: str | bool = None
    bgr_color: str | bool = None


class HavertonRegion(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    description: str | bool = None


class HavertonServiceType(BaseModel):
    uuid: str | bool
    description: str | bool


class HavertonWrPreference(BaseModel):
    uuid: str | bool = None
    name: str | bool = None


class HavertonLocation(BaseModel):
    uuid: str | bool
    name: str | bool


class HavertonDefectCategory(BaseModel):
    uuid: str | bool
    name: str | bool


class HavertonAddress(BaseModel):
    uuid: str | bool = None
    name: str | bool = None
    site_address: str | bool = None
