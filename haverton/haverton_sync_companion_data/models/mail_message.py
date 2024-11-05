
import logging

from odoo import Command, api, models
from odoo.addons.haverton_base.tools.text import get_html_plain_text

from ..companion.models import JobActivityMessage, JobMessage, Message

_logger = logging.getLogger(__file__)


class MailMessage(models.Model):
    _name = 'mail.message'
    _inherit = ['abstract.companion.data.sync', 'mail.message']

    @property
    def companion_model(self):
        return Message

    @property
    def companion_primary_column_name(self):
        return 'MessageID'

    @property
    def allow_create_new_companion_records(self):
        return all([
            self.get_allow_sync_data_to_companion_param(),
            not self.env.context.get('in_data_sync'),
        ])

    def _action_insert_sync_companion_data(self, companion_data, session):
        vals_list = self._prepare_sync_companion_data(companion_data, session)
        new_records = self._insert_sync_companion_data(vals_list)
        return new_records

    def _action_update_message(self, companion_data, res_model):
        """
        Set model, res_id for message based on res_model
        Params:
            companion_data: raws getted from Companion
            res_model: name of the Odoo model (project.project or project.task)
        """
        updated_records = self
        for rec in companion_data:
            message = self.browse_by_haverton_uuid(rec.MessageID)
            if not message:
                continue
            companion_col = rec.JobID if res_model == 'project.project' else rec.ActivityID
            res = self.env[res_model].sudo(
            ).browse_by_haverton_uuid(companion_col)
            if not res:
                continue
            message.res_id = res.id
            message.record_name = res.name
            message.model = res_model
            updated_records += message
        return updated_records

    def _action_update_job_message(self, companion_data, session):
        return self._action_update_message(companion_data, 'project.project')

    def _action_update_job_activity_message(self, companion_data, session):
        return self._action_update_message(companion_data, 'project.task')

    def _sync_companion_data(self, session):
        self._sync_companion_data_with_batch_size(
            session, Message, Message.CreatedOnUTC, self._action_insert_sync_companion_data)
        self._sync_companion_data_with_batch_size(
            session, JobMessage, JobMessage.MessageID, self._action_update_job_message)
        self._sync_companion_data_with_batch_size(
            session, JobActivityMessage, JobActivityMessage.MessageID, self._action_update_job_activity_message)

    @api.model
    def companion_field_mapping(self):
        return {
            self.companion_primary_column_name: 'haverton_uuid',
            'FromUserID': 'author_id',
            'CreatedOnUTC': 'date',
            'Subject': 'subject',
            'MessageText': 'body',
            'MessageType': 'haverton_message_type',
            'ServiceProviderID': 'partner_ids'
        }

    @api.model
    def prepare_companion_values(self, list_values, sql_session):
        res = super(MailMessage, self).prepare_companion_values(
            list_values,  sql_session)
        for value in res:
            value['is_companion_message'] = True
            note_subtype = self.env.ref('mail.mt_note')
            if note_subtype:
                value['subtype_id'] = note_subtype.id

            if 'author_id' in value:
                user = self.env['res.users'].browse_by_haverton_uuid(
                    value['author_id'])
                value['author_id'] = user.partner_id.id if user and user.partner_id else None
            if 'partner_ids' in value:
                partner = self.env['res.partner'].browse_by_haverton_uuid(
                    value['partner_ids'])
                value['partner_ids'] = [Command.link(
                    partner.id)] if partner else None
        return res

    # sync to companion
    def prepare_new_companion_record(self):
        """
        Prepare and return a new Companion record mapping with self
        """
        companion_record = super().prepare_new_companion_record()
        if companion_record.get('MessageType') is None:
            companion_record['MessageType'] = 1
        companion_record['MessageText'] = get_html_plain_text(
            companion_record['MessageText'])
        user_ids = self.author_id.user_ids
        if user_ids:
            companion_record['FromUserID'] = user_ids[0].haverton_uuid
        if not companion_record.get('FromUserID'):
            # ignore if FromUserID in companion doesn't exist
            return
        return companion_record

    def get_new_companion_records(self):
        res = super().get_new_companion_records()
        return res.filtered_domain([('is_companion_message', '=', True)])

    def _prepare_new_companion_relational_records(self, new_records):
        new_relational_records = []
        for rec in self:
            for companion_mess_rec in new_records:
                odoo_mess_res_object = self.env[rec.model].search(
                    [('id', '=', rec.res_id), ('haverton_uuid', '!=', False)], limit=1)
                if not odoo_mess_res_object:
                    continue
                if rec.model == 'project.project':
                    new_relational_records.append(JobMessage(
                        JobID=odoo_mess_res_object.haverton_uuid, MessageID=companion_mess_rec.MessageID))
                elif rec.model == 'project.task':
                    new_relational_records.append(JobActivityMessage(
                        ActivityID=odoo_mess_res_object.haverton_uuid, MessageID=companion_mess_rec.MessageID))
        return new_relational_records

    def _create_companion_records(self, session):
        # add new companion records for JobMessage, JobActivityMessage
        new_records = super()._create_companion_records(session)
        new_relational_records = self._prepare_new_companion_relational_records(
            new_records)
        if not new_relational_records:
            return new_records
        session.add_all(new_relational_records)
        session.commit()
        new_records.extend(new_relational_records)
        return new_relational_records
