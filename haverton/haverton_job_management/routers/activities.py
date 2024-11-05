from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Body, Depends
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import authorize_session
from odoo.addons.haverton_base_fastapi.schemas import (
    Message,
    MessageCreate,
    MessageCreateWithAttachment,
)
from odoo.addons.haverton_base_fastapi.utils import message as base_message_utils
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

from ..schemas import (
    JobActivity,
    JobActivityBookingMessageCreate,
    JobActivityComplete,
    JobActivityQuestionAnswerBase,
    JobMessageBase,
    JobMessageSubtypeCode,
)
from ..utils import activity as activity_utils
from ..utils import message as message_utils

router = APIRouter()


@router.get("/{uuid}", response_model=JobActivity)
def get_job_activity(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the job activity detail
    """
    activity = request.env['project.task'].validate_by_uuid(uuid)
    return activity


@router.get("/{uuid}/complete", response_model=JobActivityComplete)
def get_job_activity_complete(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the job activity complete detail.
    """
    activity = request.env['project.task'].validate_by_uuid(uuid)
    res = JobActivityComplete()
    res.from_instance(activity)
    return res


@router.post("/{uuid}/uncomplete", response_model=JobActivity)
def uncomplete_activity(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    """
    Uncomplete an activity.
    Params:
    - str uuid: The UUID of the activity to be uncompleted.
    """
    activity = activity_utils.validate_activity_uuid(uuid)
    activity.date_end = None
    return activity


@router.put("/{uuid}", response_model=JobActivity)
def update_job_activity(
        current_user: Annotated[Users | None, Depends(authorize_session)],
        uuid: str,
        booked_start_date: Annotated[datetime, Body()] = None,
        message: MessageCreate = None,
        date_end: Annotated[datetime, Body()] = None,
        question_answer_data: List[JobActivityQuestionAnswerBase] = None,
        is_complete_activity: Annotated[bool, Body()] = None):
    """
    Update activity.
    Params:
    - datetime booked_start_date, date_end: The booked start datetime in ISO 8601 format with UTC timezone. Example: "2024-03-12T12:00:00Z"
    - list[JobActivityQuestionAnswerBase] question_answer_data: A list of question answer data.
    - bool is_complete_activity: Set to true to mark it in incomplete flow.
    """
    activity = activity_utils.validate_activity_uuid(uuid)
    activity_utils.validate_update_job_activity_input(
        activity,
        booked_start_date=booked_start_date,
        message=message,
        date_end=date_end,
        question_answer_data=question_answer_data,
        is_complete_activity=is_complete_activity,
    )
    value = {}
    if booked_start_date:
        formatted_datetime = booked_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        value['booked_start_date'] = formatted_datetime
        if not activity.booked_start_date:
            # add a message when booking an activity
            booking_message = JobActivityBookingMessageCreate(
                **message.model_dump(),
                task_booked_start_date=formatted_datetime
            )
            base_message_utils.add_new_message(
                booking_message, res_object=activity, subtype_code=JobMessageSubtypeCode.booking)
    if question_answer_data:
        for answer in question_answer_data:
            activity_answer = request.env['haverton.activity.question.answer'].validate_by_uuid(answer.uuid)
            activity_answer.sudo().write(
                {
                    'is_completed': answer.is_completed,
                    'is_not_applicable': answer.is_not_applicable
                }
            )
    if is_complete_activity and date_end:
        value['date_end'] = date_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    if value:
        activity.sudo().web_save(value, specification={})
    return activity


@router.get("/{uuid}/messages", response_model=PagedCollection[JobMessageBase])
def get_activity_messages(
    paging: Annotated[Paging, Depends(paging)],
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    activity = activity_utils.validate_activity_uuid(uuid)
    return message_utils.get_messages(activity.id, paging.limit, paging.offset)


@router.post("/{uuid}/messages", response_model=Message)
def add_new_activity_message(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str,
    payload: MessageCreateWithAttachment,
):
    activity = activity_utils.validate_activity_uuid(uuid)
    return base_message_utils.add_new_message(payload, res_object=activity, subtype_code=JobMessageSubtypeCode.note)
