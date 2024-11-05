from odoo import _
from odoo.exceptions import UserError
from odoo.http import request


def validate_variation_uuid(uuid: str):
    variation = request.env['project.task'].validate_by_uuid(uuid)
    if variation.haverton_task_type != 'variation':
        raise UserError(_('This is not a variation'))
    return variation
