import logging

from odoo import _, api, models
from sqlmodel import Session, select, update, delete
from sqlalchemy import or_
from sqlalchemy import URL, create_engine
from ..companion.models import HistoryChangeData
from odoo.exceptions import UserError

_logger = logging.getLogger(__file__)

TABLE_MODEL_MAPPING = {
    'Address': 'haverton.address',
    'Jobs': 'project.project',
    'Client': 'res.partner',
    'JobActivity': 'project.task',
    'User': 'res.users',
    'JobVariation': 'project.task',
    'ServiceProvider': 'res.partner',
    'Person': 'res.partner',
    'JobActivityQuestionAnswer': 'haverton.activity.question.answer',
    'Message': 'mail.message',
    'Code': 'haverton.code',
    'JobCustomControlValue': 'project.project'
}
RELATIONAL_TABLE_MAPPING = {
    'ServiceProviderRegion': {'model': 'res.partner', 'field': 'region_ids', 'relation_model': 'haverton.region', 'haverton_relation_primary_column': 'RegionID'},
    'ServiceProviderServiceType': {'model': 'res.partner', 'field': 'service_type_ids', 'relation_model': 'haverton.service.type', 'haverton_relation_primary_column': 'ServiceTypeID'},
    'JobMessage': {'model': 'project.project', 'haverton_table_field': 'JobID', 'field': 'message_ids', 'relation_model': 'mail.message', 'haverton_relation_primary_column': 'MessageID'},
    'JobActivityMessage': {'model': 'project.task', 'field': 'message_ids', 'relation_model': 'mail.message', 'haverton_relation_primary_column': 'MessageID'},
    'JobActivityPredecessor': {'model': 'project.task', 'field': 'predecessor_ids', 'relation_model': 'project.task', 'haverton_relation_primary_column': 'PredecessorID'},
    'PersonServiceProviderRelationship': {'model': 'res.partner', 'field': 'child_ids', 'relation_model': 'res.partner', 'haverton_relation_primary_column': 'PersonID'},
    'PersonClientRelationship': {'model': 'res.partner', 'field': 'child_ids', 'relation_model': 'res.partner', 'haverton_relation_primary_column': 'PersonID'},
    'JobLocation': {'model': 'project.project', 'haverton_table_field': 'JobID', 'field': 'location_ids', 'relation_model': 'haverton.location', 'haverton_relation_primary_column': 'LocationID'},
    'DefectActivityLocation': {'model': 'project.task', 'field': 'location_ids', 'relation_model': 'haverton.location', 'haverton_relation_primary_column': 'LocationID'},
}


class AbstractCompanionHistoryData(models.AbstractModel):
    _name = 'abstract.companion.history.data'
    _description = 'Abstract Model For History Change Data'

    @property
    def history_change_data_batch_size(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.history_change_data_batch_size'
        )) or 100

    def _connection_open_sqlalchemy(self):
        try:
            company = self.env.company
            server = company.companion_db_host
            if company.companion_db_port:
                server += ',%s' % company.companion_db_port
            database = company.companion_db_database
            username = company.companion_db_username
            password = company.companion_db_password
            connection_string = 'TrustServerCertificate=YES;Encrypt=YES;DRIVER={ODBC Driver 18 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s' % (
                server, database, username, password)
            connection_url = URL.create(
                "mssql+pyodbc", query={"odbc_connect": connection_string})
            return create_engine(connection_url)
        except Exception as e:
            _logger.error(e)
            raise (UserError(e))

    @api.model
    def sync_history_data_change(self):
        engine = self._connection_open_sqlalchemy()
        with Session(engine) as session:
            history_data = session.exec(select(HistoryChangeData).where(
                or_(HistoryChangeData.status == None, HistoryChangeData.status == 'inprogress')).order_by(
                HistoryChangeData.id.asc()).limit(self.history_change_data_batch_size)).all()
            if not history_data:
                return
            history_updated_records = []
            session.execute(update(HistoryChangeData).where(HistoryChangeData.id.in_([item.id for item in history_data])).values(status="inprogress"))
            session.commit()
            for history in history_data:
                try:
                    if history.table_name in TABLE_MODEL_MAPPING.keys():
                        model = TABLE_MODEL_MAPPING.get(history.table_name)
                        if history.table_name == 'JobCustomControlValue':
                            self.env[model].sudo().with_context(in_data_sync=True).assign_history_contract_house_design(history)
                        else:
                            if history.action_name == 'insert':
                                self.env[model].sudo().with_context(is_create=True, table_name=history.table_name,
                                                                    in_data_sync=True, in_history_data_change=True).insert_companion_record(history, session)
                            elif history.action_name == 'update':
                                self.env[model].sudo().with_context(in_data_sync=True, table_name=history.table_name,
                                                                    in_history_data_change=True).update_companion_record(history, session)
                            elif history.action_name == 'delete':
                                self.env[model].sudo().with_context(
                                    in_data_sync=True, table_name=history.table_name, in_history_data_change=True).delete_companion_record(history)
                    elif history.table_name in RELATIONAL_TABLE_MAPPING.keys():
                        relation = RELATIONAL_TABLE_MAPPING.get(history.table_name)
                        self.env[relation['model']].sudo().with_context(in_data_sync=True).relation_table_history_data_change(history, relation['field'], relation['relation_model'], relation['haverton_relation_primary_column'], haverton_table_field=relation.get('haverton_table_field', False))
                    history_updated_records.append({'id': history.id, "status": "done", "note": ""})
                except Exception as e:
                    history_updated_records.append({'id': history.id, "status": "failed", "note": str(e)})
            session.execute(update(HistoryChangeData), history_updated_records)
            session.commit()

    @api.model
    def delete_done_history_data_change(self):
        engine = self._connection_open_sqlalchemy()
        with Session(engine) as session:
            session.execute(delete(HistoryChangeData).where(HistoryChangeData.status == "done"))
            session.commit()
