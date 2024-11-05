import json
import logging
import uuid
from datetime import date, datetime

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, delete, select

from ..companion import Connection

HAVERTON_COMPUTE_FIELD = {
    'res.partner': ['wr_preference_id', 'haverton_first_name', 'haverton_middle_name', 'haverton_last_name'],
    'mail.message': ['author_id'],
    'project.task': ['reason_domain', 'reason_code', 'approval_domain', 'approval_code']
}

HAVERTON_TABLE_PRIMARY_MAPPING = {
    'JobVariation': 'VariationId',
    'Person': 'PersonID',
    'Client': 'ClientID'
}

_logger = logging.getLogger(__file__)


class AbstractCompanionDataSync(models.AbstractModel):
    _name = 'abstract.companion.data.sync'
    _description = 'Abstract Model For Sync Companion Data'

    @property
    def companion_model(self):
        """
        The companion model defined in companion.models represent for self model in the Companion
        """
        return None

    @property
    def companion_primary_column_name(self):
        """
        The name of the primary column in the table in Companion
        """
        return None

    @property
    def companion_primary_columns_mapping(self):
        """
        The mapping names between the Companion primary columns and the Odoo columns.
        Used in tables contains multi primary-keys.
        """
        return None

    @property
    def companion_parent_column_name(self):
        """
        The name of column represent the parent of a record in the table in Companion.
        Used when link a record to parent_id field.
        """
        return None

    def prepare_primary_fields_values(self, companion_value: dict):
        if not self.companion_primary_columns_mapping:
            return {}
        return {v: companion_value.get(k) for k, v in self.companion_primary_columns_mapping.items()}

    def get_entity_id_by_haverton_uuid(self, model_name: str, uuid: str):
        entity = self.env[model_name].browse_by_haverton_uuid(uuid)
        return entity.id if entity else None

    def check_record_existed(self, record: object):
        return self.sudo().with_context(active_test=False).search_count(
            [('haverton_uuid', '=', getattr(record, self.companion_primary_column_name))]) > 0

    def check_allow_insert_odoo_record(self, companion_row) -> bool:
        return not self.check_record_existed(companion_row)

    def _prepare_sync_companion_data(self, companion_data, session):
        companion_mapping = self.companion_field_mapping()
        if not companion_mapping:
            return []
        vals_list = [{v: getattr(row, k) for k, v in companion_mapping.items()}
                     for row in companion_data if self.check_allow_insert_odoo_record(row)]
        if not vals_list:
            return []
        return self.prepare_companion_values(vals_list, session)

    def _insert_sync_companion_data(self, vals_list):
        if not vals_list:
            return self
        return self.with_context(in_data_sync=True).create(vals_list)

    def _link_parent_id(self, data):
        if not self.companion_parent_column_name:
            return
        for rec in data:
            parent_haverton_uuid = getattr(
                rec, self.companion_parent_column_name)
            if not parent_haverton_uuid:
                continue
            parent = self.browse_by_haverton_uuid(parent_haverton_uuid)
            if not parent:
                continue
            entity = self.browse_by_haverton_uuid(
                getattr(rec, self.companion_primary_column_name))
            if entity:
                entity.parent_id = parent.id

    def _sync_companion_data_with_batch_size(self, session, companion_model, order_by, action, condition=None):
        """
        Sync data from Companion using batch_size (Used for the large tables).
        Params:
            session: SQL session
            companion_model: The model respresent for Companion table
            order_by: The column of Companion table
            action: The function runned when the sync data progress
        """
        limit = int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.batch_size'
        )) or 100
        offset = 0
        updated_records = self
        while True:
            statement = select(companion_model)
            if condition is not None:
                statement = statement.where(condition)
            statement = statement.order_by(
                order_by).offset(offset).limit(limit)
            companion_data = session.exec(statement).all()
            batch_updated_records = action(companion_data, session)
            if batch_updated_records:
                self.env.cr.commit()
                updated_records += batch_updated_records
            _logger.info('Synchronization data of %s from %s to %s is completed.' % (
                companion_model.__tablename__, offset + 1, offset + len(companion_data)))
            if len(companion_data) < limit:
                # in the last page
                break
            offset += limit
        return updated_records

    def _sync_companion_data(self, session):
        self = self.sudo().with_context(is_create=True)
        companion_data = session.exec(select(self.companion_model)).all()
        vals_list = self._prepare_sync_companion_data(companion_data, session)
        new_records = self._insert_sync_companion_data(vals_list)
        if new_records:
            new_records._link_parent_id(companion_data)
        return new_records

    def _prepare_many2many_field(
        self,
        session,
        vals: dict,
        res_model_name: str,
        companion_model: SQLModel,
        odoo_field: str,
        companion_field: str
    ):
        """
        Prepare values for many2many field of the Odoo model
        :param session: session in SQL server
        :param vals: values of an Odoo model object
        :param res_model_name: comodel_name of the many2many field
        :param companion_model: model represent for the mapping table in Companion db
        :param odoo_field: name of many2many field
        :param companion_field: the column name represent for this field in Companion db
        :return:
        """
        companion_data = session.exec(
            select(companion_model).where(
                getattr(companion_model, self.companion_primary_column_name) == vals.get('haverton_uuid'))
        ).all()
        record_ids = []
        for rec in companion_data:
            obj = self.env[res_model_name].browse_by_haverton_uuid(
                getattr(rec, companion_field))
            if not obj:
                continue
            record_ids.append(Command.link(obj.id))
        vals[odoo_field] = record_ids
        return vals

    @api.model
    def sync_companion_data(self):
        _logger.info(_('Start sync data of %s.' % self._name))
        conn = Connection()
        engine = conn.engine
        with Session(engine) as session:
            self._sync_companion_data(session)
        _logger.info(_('Synchronization data of %s is completed.' %
                       self._name))

    @api.model
    def delete_companion_record(self, delete_data):
        if not delete_data:
            return
        companion_parent_column_name = HAVERTON_TABLE_PRIMARY_MAPPING.get(
            self.env.context.get('table_name'), self.companion_primary_column_name)
        need_delete_ids = [item[companion_parent_column_name] for item in json.loads(
            delete_data.data_before_change) if companion_parent_column_name in item]
        self.search([('haverton_uuid', '!=', False),
                    ('haverton_uuid', 'in', need_delete_ids)]).unlink()

    @api.model
    def insert_companion_record(self, insert_data, sql_session):
        if not insert_data.data_after_change:
            return
        new_records = None
        list_values = json.loads(insert_data.data_after_change)
        companion_mapping = self.companion_field_mapping()
        values_list = [{companion_mapping[key]: value for key, value in item.items() if key in companion_mapping} for
                       item in list_values]
        values_list = self.prepare_companion_values(values_list, sql_session)
        if values_list:
            new_records = self.create(values_list)
        return new_records

    @api.model
    def update_companion_record(self, update_data, sql_session):
        list_values_before = json.loads(update_data.data_before_change)
        list_values_after = json.loads(update_data.data_after_change)
        if len(list_values_before) != len(list_values_after):
            raise ValidationError(_('Invalid data'))
        updates_value_list = self.prepare_companion_update_values(
            list_values_after, list_values_before, sql_session)
        if updates_value_list:
            for update_value in updates_value_list:
                record = self.sudo().browse_by_haverton_uuid(update_value[0])
                if record:
                    record.sudo().write(update_value[1][0])

    @api.model
    def prepare_companion_update_values(self, list_values_after, list_values_before, sql_session):
        updates = []
        companion_mapping = self.companion_field_mapping()
        companion_parent_column_name = HAVERTON_TABLE_PRIMARY_MAPPING.get(
            self.env.context.get('table_name'), self.companion_primary_column_name)
        compute_field = HAVERTON_COMPUTE_FIELD.get(self._name, [])

        if not all(isinstance(item, dict) for item in list_values_after) or not all(
                isinstance(item, dict) for item in list_values_before):
            raise ValidationError(_('List elements must be dictionaries'))

        for after_item, before_item in zip(list_values_after, list_values_before):
            update = {}
            for key, value in after_item.items():
                if key in companion_mapping and (before_item.get(key) != value or companion_mapping[key] in compute_field):
                    update[companion_mapping[key]] = value
            if update:
                haverton_uuid = after_item.get(companion_parent_column_name)
                if haverton_uuid:
                    updates.append(
                        (haverton_uuid, self.prepare_companion_values([update], sql_session)))
        return updates

    @api.model
    def companion_field_mapping(self):
        """
        Contains dict represent fields mapping between Companion and Odoo
        """
        return dict()

    @property
    def companion_many2many_field_mapping(self):
        """
        Contains dict represent: many2many field >< CompanionRelationalModel
        """
        return dict()

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        updated_data_list = []
        compute_field = HAVERTON_COMPUTE_FIELD.get(self._name, [])
        for values in list_values:
            if self.env.context.get('is_create', False):
                record = self.browse_by_haverton_uuid(
                    values.get('haverton_uuid'))
                if record:
                    continue
            updated_data = {}
            for key, value in values.items():
                if isinstance(self._fields[key], fields.Datetime) and value and not isinstance(value, datetime):
                    datetime_object = self.convert_datetime_object(value)
                    updated_data[key] = datetime_object.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)
                elif isinstance(self._fields[key], fields.Date) and value and not isinstance(value, date):
                    datetime_object = self.convert_datetime_object(value)
                    updated_data[key] = datetime_object.strftime(
                        DEFAULT_SERVER_DATE_FORMAT)
                elif isinstance(self._fields[key], fields.Many2one) and key not in compute_field:
                    relation_record = self[key].browse_by_haverton_uuid(value)
                    updated_data[key] = relation_record.id if relation_record else False
                else:
                    updated_data[key] = value
            updated_data_list.append(updated_data)
        return updated_data_list

    def convert_datetime_object(self, date_string):
        formats = ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S']
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                pass
        raise ValueError("Invalid date format")

    @api.model
    def relation_table_history_data_change(self, history, relation_field, relation_model, haverton_relation_primary_column, haverton_table_field=False):
        data_before_change = history.data_before_change
        data_after_change = history.data_after_change

        def update_records(data, command):
            if not data:
                return
            list_values = json.loads(data)
            for value in list_values:
                if self.companion_primary_column_name:
                    record = self.sudo().browse_by_haverton_uuid(
                        value.get(haverton_table_field or self.companion_primary_column_name))
                elif self.companion_primary_columns_mapping:
                    record = self.browse_by_primary_fields(
                        **self.prepare_primary_fields_values(value)
                    )
                else:
                    continue
                if not record:
                    continue
                relation_record = self.env[relation_model].browse_by_haverton_uuid(
                    value.get(haverton_relation_primary_column))
                if not relation_record:
                    continue
                if relation_model == 'mail.message':
                    relation_record.model = self._name
                record.write({relation_field: [command(relation_record.id)]})
        update_records(data_before_change, Command.unlink)
        update_records(data_after_change, Command.link)

    # sync data from odoo to companion below

    def extract_companion_field_value(self, odoo_field):
        """
        Return the value of the Companion field from the Odoo field
        """
        field_value = getattr(self, odoo_field)
        if not isinstance(self._fields[odoo_field], fields.Boolean) and field_value is False:
            field_value = None
        elif isinstance(self._fields[odoo_field], fields.Many2one):
            odoo_field_haverton_uuid = getattr(field_value, 'haverton_uuid')
            if odoo_field_haverton_uuid:
                field_value = odoo_field_haverton_uuid
            else:
                field_value = None
        elif isinstance(self._fields[odoo_field], fields.Many2many):
            # many2many field will be updated after the other info was writed
            field_value = None

        return field_value

    def prepare_new_companion_record(self):
        """
        Prepare and return a new Companion record mapping with self
        """
        self.ensure_one()
        haverton_uuid = str(uuid.uuid4()).upper()
        companion_record = {
            self.companion_primary_column_name: haverton_uuid
        }
        self.with_context(in_data_sync=True).haverton_uuid = haverton_uuid
        for companion_field, odoo_field in self.companion_field_mapping().items():
            field_value = self.extract_companion_field_value(odoo_field)
            companion_record[companion_field] = field_value
        return companion_record

    def prepare_new_companion_records(self):
        """
        Prepare and return the new Companion records mapping with self
        """
        new_records = []
        for rec in self:
            if rec.haverton_uuid:
                continue
            new_companion_record = rec.prepare_new_companion_record()
            if not new_companion_record:
                continue
            new_records.append(self.companion_model(
                **new_companion_record
            ))
        return new_records

    def _create_companion_records(self, session):
        new_records = self.prepare_new_companion_records()
        if new_records:
            session.add_all(new_records)
            session.commit()
        return new_records

    def create_companion_records(self):
        """
        Create the new Companion records after the Odoo records created
        """
        conn = Connection()
        engine = conn.engine
        new_records = []
        with Session(engine) as session:
            new_records = self._create_companion_records(session)
        if self and self.companion_many2many_field_mapping:
            many2many_vals = {}
            for rec in self:
                many2many_vals.update({
                    fname: [[4, id] for id in getattr(rec, fname).ids]
                    for fname in self.companion_many2many_field_mapping.keys() if getattr(rec, fname)
                })
            if many2many_vals:
                self.write_many2many_field_to_companion(many2many_vals)
        return new_records

    def write_many2many_field_to_companion(self, vals):
        """
        Write data to the Companion Relation table after update the many2many field in Odoo
        """
        for fname, val in vals.items():
            if not isinstance(self._fields[fname], fields.Many2many):
                continue
            for data in val:
                UNLINK = 3
                LINK = 4
                companion_model_info = self.companion_many2many_field_mapping.get(
                    fname)
                if not companion_model_info:
                    continue
                companion_model = companion_model_info.model
                odoo_field = self._fields.get(fname)
                if not odoo_field:
                    continue
                field_record = self.env[odoo_field.comodel_name].browse(
                    data[1])
                if not field_record:
                    continue
                second_primary_record_uuid = getattr(
                    field_record, 'haverton_uuid')
                if not second_primary_record_uuid:
                    continue
                conn = Connection()
                engine = conn.engine
                with Session(engine) as session:
                    if data[0] == UNLINK:
                        self.unlink_many2many_field_to_companion(
                            session=session,
                            companion_model=companion_model,
                            second_primary_record_uuid=second_primary_record_uuid,
                            self_companion_primary_field=companion_model_info.self_primary,
                            second_companion_primary_field=companion_model_info.second_primary
                        )
                    elif data[0] == LINK:
                        self.link_many2many_field_to_companion(
                            session=session,
                            companion_model=companion_model,
                            second_primary_record_uuid=second_primary_record_uuid,
                            self_companion_primary_field=companion_model_info.self_primary,
                            second_companion_primary_field=companion_model_info.second_primary
                        )
                    session.commit()

    def _prepare_companion_relation_data(self, base_data):
        """
        Return payload to pass into parans when a new record created.
        Overwrite it if you want to add more info into base_dara
        """
        return base_data

    def link_many2many_field_to_companion(
        self,
        session,
        companion_model: SQLModel,
        second_primary_record_uuid: str,
        self_companion_primary_field: str,
        second_companion_primary_field: str
    ):
        """
        Add a new Companion record when link a record to many2many field
        :param session: session of Connection
        :param companion_model: model represent for the mapping table in Companion db
        :param second_primary_record_uuid: uuid of the Companion field needed to add in the Relational table
        :param self_companion_primary_field: name of the primary field belong self in the Relational table
        :param second_companion_primary_field: name of the primary field belong the linked table in the Relational table
        :return:
        """
        # check existed
        raws_existed = session.exec(
            select(companion_model).where(
                getattr(companion_model,
                        self_companion_primary_field) == self.haverton_uuid,
                getattr(
                    companion_model, second_companion_primary_field) == second_primary_record_uuid
            )
        ).all()
        if raws_existed:
            return
        # insert if not existed
        payload = self._prepare_companion_relation_data({
            self_companion_primary_field: self.haverton_uuid,
            second_companion_primary_field: second_primary_record_uuid
        })
        new_raw = companion_model(**payload)
        session.add(new_raw)

    def unlink_many2many_field_to_companion(
        self,
        session,
        companion_model: SQLModel,
        second_primary_record_uuid: str,
        self_companion_primary_field: str,
        second_companion_primary_field: str
    ):
        """
        Remove the Companion record when unlink a record out of the many2many field
        :param session: session of Connection
        :param companion_model: model represent for the mapping table in Companion db
        :param second_primary_record_uuid: uuid of the Companion field needed to remove in the Relational table
        :param self_companion_primary_field: name of the primary field belong self in the Relational table
        :param second_companion_primary_field: name of the primary field belong the linked table in the Relational table
        :return:
        """
        session.exec(
            delete(companion_model).where(
                getattr(companion_model,
                        self_companion_primary_field) == self.haverton_uuid,
                getattr(
                    companion_model, second_companion_primary_field) == second_primary_record_uuid
            )
        )

    def validate_field_update(self, odoo_field):
        """
        Validate value of odoo field
        """
        pass

    def prepare_updated_companion_records(self, session, vals):
        """
        Prepare and return the updated Companion records mapping with self based on vals
        """
        updated_records = []
        for key, value in self.companion_field_mapping().items():
            if value not in vals or not self.companion_model or value not in self.fields_must_update_to_companion:
                continue
            # TODO: discuss about update service_type
            updated_haverton_uuids = [
                rec.haverton_uuid for rec in self if rec.haverton_uuid]
            statement = select(self.companion_model).where(
                getattr(self.companion_model, self.companion_primary_column_name).in_(updated_haverton_uuids))
            raws = session.exec(statement).all()
            if not raws:
                continue
            for raw in raws:
                self.validate_field_update(value)
                new_val = self.extract_companion_field_value(value)
                setattr(raw, key, new_val)
                updated_records.append(raw)
        return updated_records

    def update_companion_records(self, vals):
        """
        Update the mapping Companion records after the Odoo records updated
        """
        if not self.companion_field_mapping() or not self.companion_primary_column_name:
            return
        conn = Connection()
        engine = conn.engine
        with Session(engine) as session:
            updated_records = self.prepare_updated_companion_records(
                session, vals)
            if updated_records:
                session.add_all(updated_records)
                session.commit()
        self.write_many2many_field_to_companion(vals)
        return updated_records

    @property
    def fields_must_update_to_companion(self):
        """
        Return fields must be updated to Companion
        """
        return []

    @property
    def allow_create_new_companion_records(self):
        """
        Check whether the self model can create a new Companion record or not
        """
        return False

    def get_allow_sync_data_to_companion_param(self):
        return bool(int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.allow_sync_data_to_companion'
        ) or 0))

    def check_allow_update_companion_records(self, vals):
        """
        Check whether the self model can update a Companion record or not
        """
        if any([
            not self.get_allow_sync_data_to_companion_param(),
            self.env.context.get('in_data_sync'),
            not self.fields_must_update_to_companion,
        ]):
            return False
        for key in vals.keys():
            if key in self.fields_must_update_to_companion:
                # allow update
                return True
        return False

    def get_new_companion_records(self):
        return self

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        companion_records = res.get_new_companion_records()
        if companion_records and companion_records.allow_create_new_companion_records:
            try:
                companion_records.create_companion_records()
            except SQLAlchemyError as e:
                log = request.env.context.get('companion_sync_log')
                if log:
                    log.save_companion_sync_log_error(e)
        return res

    def get_update_companion_records(self):
        return self.filtered_domain([('haverton_uuid', '!=', False)])

    def write(self, vals):
        res = super().write(vals)
        companion_records = self.get_update_companion_records()
        if companion_records and companion_records.check_allow_update_companion_records(vals):
            try:
                companion_records.update_companion_records(vals)
            except SQLAlchemyError as e:
                log = request.env.context.get('companion_sync_log')
                if log:
                    log.save_companion_sync_log_error(e)
        return res
