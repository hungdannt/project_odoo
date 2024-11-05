import base64
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, status
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.http import request

from ..dependencies import authorize_session, format_query
from ..schemas import User, UserMentionSuggestion, UserMenuItem

router = APIRouter()


@router.get("/me", response_model=User)
def get_current_user(current_user: Annotated[Users | None, Depends(authorize_session)]):
    """
    Get information of the current user
    """
    return current_user


@router.put("/me", response_model=User)
def update_current_user(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        avatar: UploadFile = None,
        main_menu_key: Annotated[str, Body()] = None):
    """
    Update information of the current user.
    Params:
    - avatar: The file represent for the user avatar.
    - main_menu_key: The Haverton menu key represent for the main menu item belong a user.
    """
    updated_data = {}
    if avatar:
        updated_data['image_1920'] = base64.b64encode(avatar.file.read())
    if main_menu_key:
        updated_data['main_haverton_menu_key'] = main_menu_key
    if updated_data:
        current_user.web_save(updated_data, specification={})
    return current_user


@router.get('/me/menu', response_model=list[UserMenuItem])
def get_user_menu(current_user: Annotated[Users | None, Depends(authorize_session)]):
    """
    Get the menu items visible to the current user
    """
    res = request.env['ir.ui.menu'].web_search_read(
        domain=[('active', '=', True), ('mobile_visibility', '=', True)],
        specification={'name': {}, 'haverton_menu_key': {}}
    )
    menu_items = res.get('records', [])
    return [UserMenuItem.from_menu_item(i) for i in menu_items]


@router.put("/{uuid}", response_model=User, deprecated=True)
def update(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        uuid: str,
        avatar: UploadFile = None,
        main_menu_key: Annotated[str, Body()] = None):
    """
    Update information of the current user.
    Params:
    - avatar: The file represent for the user avatar.
    - main_menu_key: The Haverton menu key represent for the main menu item belong a user.
    """
    # TODO: This API is replaced by update_current_user. Remove this API after all user used new version app
    if current_user.uuid != uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    updated_data = {}
    if avatar:
        updated_data['image_1920'] = base64.b64encode(avatar.file.read())
    if main_menu_key:
        updated_data['main_haverton_menu_key'] = main_menu_key
    if updated_data:
        current_user.web_save(updated_data, specification={})
    return current_user


@router.get("/mention_suggestions", response_model=PagedCollection[UserMentionSuggestion])
def get_mention_suggestions(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        q: Annotated[str, Depends(format_query)] = None):
    """
    Get the users as the mention suggestions.
    """
    domain = [
        *request.env['res.users'].haverton_active_domain,
        ('name', 'ilike', q),
    ]
    specification = dict(UserMentionSuggestion())
    res = request.env['res.users'].with_context(haverton_search=True).web_search_read(
        domain=domain,
        specification=specification,
        order='name asc',
        limit=paging.limit,
        offset=paging.offset
    )
    count = request.env['res.users'].search_count(domain=domain)
    return PagedCollection[UserMentionSuggestion](
        count=count,
        items=res['records']
    )
