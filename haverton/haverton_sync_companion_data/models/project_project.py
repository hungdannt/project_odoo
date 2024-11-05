import json

from odoo import Command, api, models
from sqlmodel import Session, select

from ..companion import Connection
from ..companion.models import JobActivity, JobCustomControlValue, JobLocation, Jobs


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['abstract.companion.data.sync', 'project.project']

    @property
    def companion_model(self):
        return Jobs

    @property
    def companion_primary_column_name(self):
        return 'JobId'

    def _assign_contract_house_design(self, session):
        contract_house_design_uuid = self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.contract_house_design_uuid'
        )
        if not contract_house_design_uuid:
            return
        rows = session.exec(select(JobCustomControlValue).where(
            JobCustomControlValue.CustomControlID == contract_house_design_uuid))
        for row in rows:
            job = self.filtered_domain([('haverton_uuid', '=', row.JobID)])
            if not job:
                return
            job.contract_house_design = row.Text

    def _prepare_location_ids(self, session, vals_list):
        for vals in vals_list:
            companion_data = session.exec(select(JobLocation).where(
                JobLocation.JobID == vals.get('haverton_uuid'))).all()
            location_ids = []
            for rec in companion_data:
                location = self.env['haverton.location'].browse_by_haverton_uuid(
                    rec.LocationID)
                if not location:
                    continue
                location_ids.append(Command.link(location.id))
            vals['location_ids'] = location_ids
        return vals_list

    def _sync_companion_data(self, session):
        companion_data = session.exec(select(self.companion_model)).all()
        vals_list = self._prepare_sync_companion_data(companion_data, session)
        vals_list = self._prepare_location_ids(session, vals_list)
        new_records = self._insert_sync_companion_data(vals_list)
        if new_records:
            new_records._link_parent_id(companion_data)
            new_records._assign_contract_house_design(session)
        return new_records

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'ContractNo': 'contract_no',
            'ClientID': 'client_id',
            'AddressID': 'address_id',
            'StartDate': 'date_start',
            'EndDate': 'date',
            'RegionID': 'region_id',
            'ContractValueExGST': 'contract_value_ex_gst',
            'ContractValueIncGST': 'contract_value_inc_gst',
            'ContractStartDateDenormalised': 'contract_start_on',
            'ContractEndDateDenormalised': 'contract_end_on',
            'LastUpdatedOnUTC': 'haverton_write_date',
            'LastUpdatedBy': 'write_user_name',
            'WorkflowStatusID': 'stage_id',
            'DocumentDirectoryNumber': 'document_directory_number',
        }

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        res = super(ProjectProject, self).prepare_companion_values(list_values,  sql_session)
        for value in res:
            if 'date' in value:
                value['est_date'] = value['date']
        return res

    def assign_history_contract_house_design(self, history_data):
        if not history_data.data_after_change:
            return
        update_data = json.loads(history_data.data_after_change)
        contract_house_design_uuid = self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.contract_house_design_uuid'
        )
        for data in update_data:
            if not data.get('CustomControlID') == contract_house_design_uuid:
                continue
            job = self.sudo().browse_by_haverton_uuid(data.get('JobID'))
            if job:
                job.contract_house_design = data.get('Text')

    def get_latest_task_sequence(self, haverton_task_type: str):
        latest_sequence = super().get_latest_task_sequence(haverton_task_type)
        if haverton_task_type == 'defect' and self.get_allow_sync_data_to_companion_param():
            conn = Connection()
            engine = conn.engine
            with Session(engine) as session:
                latest_sequence = session.exec(select(JobActivity.Sequence).where(
                    JobActivity.DefectType != None, JobActivity.JobID == self.haverton_uuid).order_by(JobActivity.Sequence.desc())).first()
        return latest_sequence or 0
