from typing import Annotated

from fastapi import APIRouter, Depends, Query
from odoo.addons.base.models.res_users import Users
from odoo.addons.base_fastapi.dependencies import paging
from odoo.addons.base_fastapi.schemas import PagedCollection, Paging
from odoo.addons.haverton_base_fastapi.dependencies import (
    authorize_session,
    format_query,
)
from odoo.addons.haverton_base_fastapi.schemas import (
    Message,
    MessageCreateWithAttachment,
    OrderBy,
)
from odoo.addons.haverton_base_fastapi.utils import message as base_message_utils
from odoo.addons.haverton_service_provider.schemas import Client, ClientBase
from odoo.http import request

from ..schemas import (
    DefectBase,
    Job,
    JobActivityBase,
    JobActivityFilterStatus,
    JobBase,
    JobFilterStatus,
    JobMasterDataField,
    JobMessageBase,
    JobMessageSubtypeCode,
    JobSearch,
    JobSortBy,
    JobStatus,
    JobVariationBase,
)
from ..utils import defect as defect_utils
from ..utils import job as job_utils
from ..utils import master_data as master_data_utils
from ..utils import message as message_utils

router = APIRouter()


@router.get("/masterdata", response_model=PagedCollection[dict])
def get_job_masterdata(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        master_field: JobMasterDataField = JobMasterDataField.user,
        q: Annotated[str, Depends(format_query)] = None,
        job_uuids: Annotated[list[str] | None, Query()] = []):
    """
    Get masterdata of the job on the user.
    """
    res_model, res_field = master_data_utils.get_job_masterdata_info(master_field)
    if not res_model:
        return PagedCollection[dict](
            count=0,
            items=[]
        )
    sort_by = None
    if master_field == JobMasterDataField.workflow_status:
        sort_by = 'sequence'
    domain = [('haverton_uuid', '!=', False)]
    if master_field == JobMasterDataField.user:
        domain = request.env['res.users'].haverton_active_domain
        if job_uuids:
            user_ids = request.env['project.project'].browse_by_uuids(job_uuids).mapped('task_ids.user_id.id')
            domain.append(('id', 'in', user_ids))
    record, total = master_data_utils.get_masterdata(
        res_model, res_field, paging.limit, paging.offset, domain=domain, query=q, sort_by=sort_by)
    return PagedCollection[dict](
        count=total,
        items=record
    )


@router.get("/", response_model=PagedCollection[JobBase])
def get_jobs(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        q: Annotated[str, Depends(format_query)] = None,
        search_field: JobSearch = None,
        status: Annotated[list[JobFilterStatus] | None, Query()] = [],
        job_status: Annotated[list[str] | None, Query()] = [],
        user_uuids: Annotated[list[str] | None, Query()] = [],
        job_uuids: Annotated[list[str] | None, Query()] = [],
        sort_by: Annotated[list[JobSortBy] |
                           None, Query()] = [JobSortBy.haverton_write_date],
        order_by: OrderBy = OrderBy.asc):
    """
    Get list of the job.
    Params:
    - q: key to search
    - search_field: field to search
    - status: status to filter
    - sort_by: fields to sort
    - order_by: order to sort
    """
    if not status:
        return PagedCollection[JobBase](
            count=0,
            items=[]
        )
    domain = job_utils.get_jobs_domain(
        search_kwargs={'q': q, 'search_field': search_field},
        filter_kwargs={'status': status, 'user_uuids': user_uuids, 'job_status': job_status, 'job_uuids': job_uuids})
    specification = dict(JobBase())
    specification['stage_id'] = {'fields': dict(JobStatus())}
    specification['client_id'] = {'fields': dict(ClientBase())}
    res = request.env['project.project'].with_context(haverton_search=True).web_search_read(
        domain=domain,
        specification=specification,
        order=','.join(map(lambda i: i.value + ' ' + order_by.value, sort_by)),
        limit=paging.limit,
        offset=paging.offset
    )
    count = request.env['project.project'].search_count(domain=domain)
    return PagedCollection[JobBase](
        count=count,
        items=res['records']
    )


@router.get("/{uuid}/activities", response_model=PagedCollection[JobActivityBase])
def get_job_activities(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        uuid: str,
        sequence: int = None,
        user_uuids: Annotated[list[str] | None, Query()] = [],
        activity_uuids: Annotated[list[str] | None, Query()] = [],
        q: Annotated[str, Depends(format_query)] = None,
        not_completed: bool = None,  # stage
        booked_start: bool = None,  # booked_start_date
        not_confirmed: bool = None,  # booking_status
        order_by: OrderBy = OrderBy.asc):
    """
    Get list of the job.
    Params:
    - **q**: key to search
    - **activity_uuids**: list of the activity uuid to filter
    - **not_completed**: stage to filter
    - **booked_start**: booked_start_date to filter
    - **not_confirmed**: booking_status to filter
    - **sequence**: sequence to filter
    - **order_by**: order to sort
    """
    job = request.env['project.project'].validate_by_uuid(uuid)
    domain = [
        *request.env['project.task'].single_activity_domain,
        ('project_id', '=', job.id)
    ]
    domain += job_utils.get_job_activities_domain(
        search_kwargs={'q': q},
        filter_kwargs={
            'not_completed': not_completed,
            'booked_start': booked_start,
            'not_confirmed': not_confirmed,
            'sequence': sequence,
            'user_uuids': user_uuids,
            'activity_uuids': activity_uuids,
        })
    specification = dict(JobActivityBase())
    specification['stage_id'] = {'fields': {'name': {}}}
    res = request.env['project.task'].with_context(haverton_search=True).web_search_read(
        domain=domain,
        specification=specification,
        order='sequence ' + order_by.value,
        limit=paging.limit,
        offset=paging.offset
    )
    count = request.env['project.task'].search_count(domain=domain)
    return PagedCollection[JobActivityBase](
        count=count,
        items=res['records']
    )


@router.get("/{uuid}", response_model=Job)
def get_job(current_user: Annotated[Users | None, Depends(authorize_session)], uuid: str):
    """
    Get the job detail
    """
    return request.env['project.project'].validate_by_uuid(uuid)


@router.get("/{uuid}/summary")
def get_job_summary(current_user: Annotated[Users | None,
                    Depends(authorize_session)],
                    uuid: str,
                    not_completed: bool = None,  # stage
                    booked_start: bool = None,  # booked_start_date
                    not_confirmed: bool = None,  # booking_status
                    service_type_uuid: str = None,
                    all_approvals: bool = False,
                    list_approvals: Annotated[list[str] | None, Query()] = None,
                    ):
    """
    Get the job summary detail
    """
    job = request.env['project.project'].validate_by_uuid(uuid)
    activity_domain = request.env['project.task'].single_activity_domain
    activity_domain += job_utils.get_job_activities_domain(
        search_kwargs={},
        filter_kwargs={
            'not_completed': not_completed,
            'booked_start': booked_start,
            'not_confirmed': not_confirmed
        })

    defects_domain = [('haverton_task_type', '=', 'defect')]
    if service_type_uuid:
        defects_domain.append(('service_type.uuid', '=', service_type_uuid))
    
    variants_domain = [('haverton_task_type', '=', 'variation')]
    if not all_approvals and list_approvals:
        variants_domain.append(('approval_id.code_number', 'in', [
            job_utils.APPROVALS_CODE_MAPPING[status] for status in list_approvals]))
    return {
        "total_activities": len(job.task_ids.filtered_domain(activity_domain)),
        "total_defects": len(job.task_ids.filtered_domain(defects_domain)),
        "total_variants": len(job.task_ids.filtered_domain(variants_domain)),
        "is_completed_by_user": job.is_completed_by_user,
        "contract_no": job.contract_no,
    }


@router.get("/{uuid}/defects", response_model=PagedCollection[DefectBase])
def get_defects(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        q: Annotated[str, Depends(format_query)] = None,
        uuid: str = None,
        defect_uuids: Annotated[list[str] | None, Query()] = [],
        status: Annotated[list[JobActivityFilterStatus] | None, Query()] = [],
        service_type_uuid: str = None,
        order_by: OrderBy = OrderBy.asc):
    """
        Get a list of defects.
        Params:
        - q: Key to search.
        - order_by: Order to sort.
        - uuid: uuid of job.
        - status: list of the defect status to filter.
        - service_type_uuid: the service type uuid to filter.
        - defect_uuids: list of the defect uuid to filter
    """
    job = request.env['project.project'].validate_by_uuid(uuid)
    domain = [('project_id', '=', job.id), ('haverton_task_type', '=', 'defect')]
    domain += job_utils.get_job_defects_domain(
        search_kwargs={'q': q},
        filter_kwargs={
            'service_type_uuid': service_type_uuid,
            'defect_uuids': defect_uuids,
        })
    res = request.env['project.task'].with_context(haverton_search=True).web_search_read(
        domain=domain,
        specification=dict(DefectBase()),
        order='sequence ' + order_by.value,
    )
    paginated_records, count = defect_utils.paginate_and_filter_by_status(res['records'], paging, status)
    return PagedCollection[DefectBase](
        count=count,
        items=paginated_records
    )


@router.get("/{uuid}/variations", response_model=PagedCollection[JobVariationBase])
def get_variations(
        paging: Annotated[Paging, Depends(paging)],
        current_user: Annotated[Users | None, Depends(authorize_session)],
        q: Annotated[str, Depends(format_query)] = None,
        all_approvals: bool = None,
        list_approvals: Annotated[list[str] | None, Query()] = None,
        variation_uuids: Annotated[list[str] | None, Query()] = [],
        uuid: str = None,
        order_by: OrderBy = OrderBy.asc):
    """
        Get a list of variations.
        Params:
        - q: Key to search.
        - order_by: Order to sort.
        - uuid: uuid of job.
        - list_approvals: a list of strings with values in ["pending", "accepted", "declined", "cancelled", "requested_by_customers", "requested", "completed"]
        - variation_uuids: list of the variation uuid to filter
    """
    job = request.env['project.project'].validate_by_uuid(uuid)
    domain = [('project_id', '=', job.id),
              ('haverton_task_type', '=', 'variation')]
    domain += job_utils.get_job_variations_domain(
        search_kwargs={'q': q},
        filter_kwargs={
            'all_approvals': all_approvals,
            'list_approvals': list_approvals,
            'variation_uuids': variation_uuids,
        })

    specification = dict(JobVariationBase())
    specification['approval_id'] = {'fields': {'name': {}}}
    specification['reason_id'] = {'fields': {'name': {}}}
    res = request.env['project.task'].with_context(haverton_search=True).sudo().web_search_read(
        domain=domain,
        specification=specification,
        order='reference ' + order_by.value,
        limit=paging.limit,
        offset=paging.offset
    )
    count = request.env['project.task'].sudo().search_count(domain=domain)
    return PagedCollection[JobVariationBase](
        count=count,
        items=res['records']
    )


@router.get("/{uuid}/messages", response_model=PagedCollection[JobMessageBase])
def get_job_messages(
    paging: Annotated[Paging, Depends(paging)],
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    job = request.env['project.project'].validate_by_uuid(uuid)
    return message_utils.get_messages(job.id, paging.limit, paging.offset)


@router.post("/{uuid}/messages", response_model=Message)
def add_new_job_message(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str,
    payload: MessageCreateWithAttachment,
):
    job = request.env['project.project'].validate_by_uuid(uuid)
    return base_message_utils.add_new_message(payload, res_object=job, subtype_code=JobMessageSubtypeCode.note)


@router.get("/{uuid}/client", response_model=Client)
def get_job_client(
    current_user: Annotated[Users | None, Depends(authorize_session)],
    uuid: str
):
    job = request.env['project.project'].validate_by_uuid(uuid)
    return job.client_id
