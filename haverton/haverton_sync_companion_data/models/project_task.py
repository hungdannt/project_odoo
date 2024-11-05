import logging

from odoo import Command, _, api, models
from odoo.exceptions import UserError
from sqlmodel import Session, select

from ..companion import Connection
from ..companion.models import (
    CompanionRelationalModel,
    DefectActivityLocation,
    JobActivity,
    JobActivityPredecessor,
    JobVariation,
    Service,
)

HAVERTON_TABLE_TASK_TYPE_MAPPING = {
    'JobActivity': 'activity',
    'JobVariation': 'variation'
}

_logger = logging.getLogger(__file__)


class ProjectTask(models.Model):
    """
    This model include data in the companion tables: JobActivity, JobVariation.
    """
    _name = 'project.task'
    _inherit = ['abstract.companion.data.sync', 'project.task']

    @property
    def companion_model(self):
        return JobActivity

    @property
    def companion_primary_column_name(self):
        return 'ActivityID'

    @property
    def fields_must_update_to_companion(self):
        return [
            'booked_start_date',
            'date_end',
            'project_id',
            'job_activity_id',
            'sequence',
            'haverton_create_date',
            'booked_start_date',
            'forecasted_start_date',
            'start_date',
            'date_end',
            'date_deadline',
            'service_provider_id',
            'user_id',
            'haverton_defect_category_id',
            'booking_confirmed_on',
            'defect_action',
            'defect_description',
            'defect_details',
            'is_back_charge',
            'work_day_duration',
            'charge_to',
            'defect_amount',
            'create_by',
            'defect_type_id',
            'location_ids',
        ]

    @property
    def allow_create_new_companion_records(self):
        return all([
            self.get_allow_sync_data_to_companion_param(),
            not self.env.context.get('in_data_sync'),
        ])

    def get_new_companion_records(self):
        res = super().get_new_companion_records()
        return res.filtered_domain([('haverton_task_type', '=', 'defect')])

    def _link_job_activity_id(self, session):
        _logger.info('Start link job_activity_id.')
        batch_size = int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.batch_size'
        )) or 100
        offset = 0
        while True:
            updated_count = 0
            companion_data = session.exec(
                select(JobActivity.ActivityID, JobActivity.LinkedJobActivity).where(
                    JobActivity.LinkedJobActivity != None).order_by(
                    JobActivity.CreatedOnUTC).offset(offset).limit(batch_size)
            ).all()
            for rec in companion_data:
                activity = self.browse_by_haverton_uuid(rec.ActivityID)
                linked_activity = self.browse_by_haverton_uuid(
                    rec.LinkedJobActivity)
                if linked_activity:
                    activity.job_activity_id = linked_activity.id
                    updated_count += 1
            if updated_count:
                self.env.cr.commit()
            if len(companion_data) < batch_size:
                # in the last page
                break
            offset += batch_size
        _logger.info('Link job_activity_id is completed.')

    def _prepare_link_job_activity_id(self, data):
        vals_list = [{
            'haverton_uuid': getattr(rec, self.companion_primary_column_name),
            'job_activity_id': rec.LinkedJobActivity,
        } for rec in data if rec.LinkedJobActivity]
        return vals_list

    def _prepare_companion_activity_values(self, companion_data, session):
        vals_list = self._prepare_sync_companion_data(companion_data, session)
        for vals in vals_list:
            self._prepare_many2many_field(
                session, vals, 'haverton.location', DefectActivityLocation, 'location_ids', 'LocationID')
        return vals_list

    def _action_sync_job_variation_to_odoo(self, companion_data, session):
        vals_list = self.with_context(table_name=JobVariation.__tablename__)._prepare_sync_companion_data(
            companion_data, session)
        return self._insert_sync_companion_data(vals_list)

    def _action_sync_job_activity_to_odoo(self, companion_data, session):
        vals_list = self.with_context(table_name=JobActivity.__tablename__)._prepare_companion_activity_values(
            companion_data, session)
        return self._insert_sync_companion_data(vals_list)

    def _sync_companion_data(self, session):
        self = self.sudo().with_context(is_create=True)
        self._sync_companion_data_with_batch_size(
            session, JobVariation, JobVariation.CreatedOnUTC, self._action_sync_job_variation_to_odoo)
        self._sync_companion_data_with_batch_size(
            session, JobActivity, JobActivity.CreatedOnUTC, self._action_sync_job_activity_to_odoo)
        self._link_job_activity_id(session)
        self._link_predecessor_ids(session)

    def _link_predecessor_ids(self, session):
        _logger.info('Start link predecessor_ids.')
        for rec in self.with_context(active_test=False).search([('haverton_task_type', 'in', ['activity', 'defect'])]):
            if not rec.haverton_uuid:
                continue
            companion_data = session.exec(
                select(JobActivityPredecessor).where(JobActivityPredecessor.ActivityID == rec.haverton_uuid)
            ).all()
            predecessor_haverton_uuids = [obj.PredecessorID for obj in companion_data]
            predecessors = self.browse_by_haverton_uuids(predecessor_haverton_uuids)
            if predecessors:
                rec.write({
                    'predecessor_ids': [Command.link(id) for id in predecessors.ids]
                })
                self.env.cr.commit()
        _logger.info('Link predecessor_ids is completed.')

    @property
    def companion_activity_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'JobID': 'project_id',
            'VariationId': 'parent_id',
            'Sequence': 'sequence',
            'CreatedOnUTC': 'haverton_create_date',
            'CreatedBy': 'create_by',
            'BookedStartDate': 'booked_start_date',
            'ForecastedStartDate': 'forecasted_start_date',
            'StartDate': 'start_date',
            'CompletionDate': 'date_end',
            'ForecastedCompletionDate': 'date_deadline',
            'ServiceProviderID': 'service_provider_id',
            'UserID': 'user_id',
            'LinkedJobActivity': 'job_activity_id',
            'DefectCategoryID': 'haverton_defect_category_id',
            'DefectType': 'defect_type_id',
            'BookingConfirmedOn': 'booking_confirmed_on',
            'ServiceID': 'haverton_service_uuid',
            'DefectAction': 'defect_action',
            'DefectDescription': 'defect_description',
            'DefectDetail': 'defect_details',
            'IsBackCharged': 'is_back_charge',
            'Duration': 'work_day_duration',
            'BackChargedServiceProviderID': 'charge_to',
            'BackChargedAmount': 'defect_amount',
            'haverton_task_type': 'haverton_task_type',
        }

    @property
    def companion_variation_field_mapping(self):
        return {
            'VariationId': 'haverton_uuid',
            'JobId': 'project_id',
            'Summary': 'name',
            'VariationNumber': 'sequence',
            'StartDate': 'start_date',
            'CreatedOnUTC': 'haverton_create_date',
            'Reference': 'reference',
            'InvoiceNumber': 'invoice_number',
            'VariationApprovalLastUpdatedBy': 'approval_last_updated_by',
            'VariationReasonDomain': 'reason_domain',
            'VariationReasonCode': 'reason_code',
            'VariationApprovalDomain': 'approval_domain',
            'VariationApprovalCode': 'approval_code',
            'CreatedBy': 'create_by',
            'haverton_task_type': 'haverton_task_type',
        }

    def companion_field_mapping(self):
        table_name = self.env.context.get('table_name')
        if self.haverton_task_type == 'variation' or (table_name and table_name.lower() == JobVariation.__tablename__):
            return self.companion_variation_field_mapping
        return self.companion_activity_field_mapping

    @property
    def companion_many2many_field_mapping(self):
        return {
            'predecessor_ids': CompanionRelationalModel(
                model=JobActivityPredecessor,
                self_primary='ActivityID',
                second_primary='PredecessorID',
            ),
            'successor_ids': CompanionRelationalModel(
                model=JobActivityPredecessor,
                self_primary='PredecessorID',
                second_primary='ActivityID',
            ),
            'location_ids': CompanionRelationalModel(
                model=DefectActivityLocation,
                self_primary='ActivityID',
                second_primary='LocationID',
            ),
        }

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        res = super(ProjectTask, self).prepare_companion_values(
            list_values,  sql_session)
        for value in res:
            if self.env.context.get('is_create', False) and self.env.context.get('in_history_data_change', False):
                if value.get('haverton_defect_category_id', False):
                    value['haverton_task_type'] = 'defect'
                elif self.env.context.get('table_name'):
                    value['haverton_task_type'] = HAVERTON_TABLE_TASK_TYPE_MAPPING.get(
                        self.env.context.get('table_name'))
            if 'reason_domain' in value or 'reason_code' in value:
                reason = self.env['haverton.code'].browse_by_domain_and_code_number(
                    value['reason_domain'], value['reason_code']
                )
                value['reason_id'] = reason.id if reason else None
            if 'approval_domain' in value or 'approval_code' in value:
                approval = self.env['haverton.code'].browse_by_domain_and_code_number(
                    value['approval_domain'], value['approval_code']
                )
                value['approval_id'] = approval.id if approval else None
            if value.get('haverton_service_uuid', False):
                if value.get('haverton_task_type') == 'defect':
                    value['name'] = value.get('defect_description')
                haverton_services = sql_session.exec(select(Service.Description, Service.ServiceTypeID).where(
                    Service.ServiceID == value.get('haverton_service_uuid'))).all()
                if not haverton_services:
                    value['name'] = value.get('name') or ' '
                    continue
                if not value.get('name'):
                    value['name'] = haverton_services[0].Description
                value['service_type'] = self.get_entity_id_by_haverton_uuid(
                    'haverton.service.type', haverton_services[0].ServiceTypeID)
        return res

    def validate_field_update(self, odoo_field):
        if odoo_field == 'parent_id':
            parent = getattr(self, 'parent_id')
            if parent and getattr(parent, 'haverton_task_type') != 'variation':
                raise UserError(_('Parent must be a Variation!'))
        elif odoo_field == 'job_activity_id':
            activity = getattr(self, 'job_activity_id')
            if getattr(activity, 'haverton_task_type') != 'activity':
                raise UserError(_('Linked Job Activity must be am Activity!'))
        return super().validate_field_update(odoo_field)

    def _prepare_companion_relation_data(self, base_data):
        payload = super()._prepare_companion_relation_data(base_data)
        activity_uuid = payload.get('ActivityID')
        if activity_uuid:
            job_uuid = None
            conn = Connection()
            engine = conn.engine
            with Session(engine) as session:
                res = session.exec(select(JobActivity.JobID).where(
                    JobActivity.ActivityID == activity_uuid)).all()
                if res:
                    job_uuid = res[0]
                    payload['JobID'] = job_uuid
        return payload

    def check_record_existed(self, record: object):
        table_name = self.env.context.get('table_name')
        if table_name and table_name.lower() == JobVariation.__tablename__:
            return self.sudo().with_context(active_test=False).search_count(
                [('haverton_uuid', '=', getattr(record, 'VariationId'))]) > 0
        return super().check_record_existed(record)

    @property
    def default_activity_haverton_service_uuid(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.default_activity_haverton_service_uuid'
        )

    @property
    def default_defect_haverton_service_uuid(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.default_defect_haverton_service_uuid'
        )

    def prepare_creation_vals_list(self, vals_list):
        vals_list = super().prepare_creation_vals_list(vals_list)
        if self.env.context.get('in_data_sync') or not self.get_allow_sync_data_to_companion_param():
            return vals_list
        for vals in vals_list:
            # set default value for haverton_service_uuid field when create an activity or a defect in Odoo
            haverton_task_type = vals.get('haverton_task_type')
            if haverton_task_type == 'activity':
                vals['haverton_service_uuid'] = self.default_activity_haverton_service_uuid
            elif haverton_task_type == 'defect':
                vals['haverton_service_uuid'] = self.default_defect_haverton_service_uuid
        return vals_list
