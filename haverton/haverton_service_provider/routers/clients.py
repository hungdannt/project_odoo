from typing import Annotated

from fastapi import APIRouter, Depends
from odoo import _
from odoo.addons.base.models.res_users import Users
from odoo.addons.haverton_base_fastapi.dependencies import authorize_session
from odoo.exceptions import UserError
from odoo.http import request

from ..schemas import Client

router = APIRouter()


@router.get("/{uuid}", response_model=Client)
def get_client(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the client detail
    """
    client = request.env['res.partner'].with_context(
        active_test=False).validate_by_uuid(uuid).filtered_domain(
            [('haverton_contact_type', '=', 'client')])
    if not client:
        raise UserError(_("Client is not found."))
    return client
