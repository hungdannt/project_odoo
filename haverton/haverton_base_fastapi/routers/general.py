from fastapi import APIRouter
from odoo.http import request

router = APIRouter()


@router.get("/support")
def get_support_content():
    return {'detail': request.env.user.company_id.support_content or ''}
