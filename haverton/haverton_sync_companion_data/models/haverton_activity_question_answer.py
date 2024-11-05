import logging

from odoo import api, models
from sqlmodel import select

from ..companion.models import JobActivityQuestionAnswer

_logger = logging.getLogger(__file__)


class HavertonActivityQuestionAnswer(models.Model):
    _name = 'haverton.activity.question.answer'
    _inherit = ['abstract.companion.data.sync',
                'haverton.activity.question.answer']

    @property
    def companion_model(self):
        return JobActivityQuestionAnswer

    def _prepare_sync_companion_data(self, data, session):
        vals_list = []
        for rec in data:
            record_existed = self.with_context(active_test=False).search_count(
                [('haverton_question_uuid', '=', rec.QuestionID), ('haverton_activity_uuid', '=', rec.ActivityID)]) > 0
            if record_existed:
                continue
            question = self.env['haverton.service.question'].browse_by_haverton_uuid(
                rec.QuestionID)
            task = self.env['project.task'].browse_by_haverton_uuid(
                rec.ActivityID)
            vals_list.append({
                'haverton_question_uuid': rec.QuestionID,
                'haverton_activity_uuid': rec.ActivityID,
                'question_id': question.id if question else None,
                'task_id': task.id if task else None,
                'is_completed': rec.Completed,
                'is_not_applicable': rec.NotApplicable,
                'note': rec.Note,
            })
        return vals_list

    def _sync_companion_data(self, session):
        offset = 0
        limit = int(self.env['ir.config_parameter'].sudo().get_param(
            'haverton_sync_companion_data.batch_size'
        )) or 100
        while True:
            companion_data = session.exec(select(self.companion_model).order_by(
                JobActivityQuestionAnswer.ActivityID).offset(offset).limit(limit)).all()
            vals_list = self._prepare_sync_companion_data(companion_data, session)
            batch_new_records = self._insert_sync_companion_data(vals_list)
            if batch_new_records:
                self.env.cr.commit()
            _logger.info('Synchronization data of %s from %s to %s is completed.' % (
                self._name, offset + 1, offset + len(companion_data)))
            if len(companion_data) < limit:
                # in the last page
                break
            offset += limit

    @api.model
    def companion_field_mapping(self):
        return {
            'QuestionID': 'question_id',
            'ActivityID': 'task_id',
            'Completed': 'is_completed',
            'NotApplicable': 'is_not_applicable',
            'Note': 'note'
        }
