import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HavertonServiceQuestion(models.Model):
    _description = 'Haverton Service Question'
    _inherit = 'haverton.service.question'

    is_inspection_question = fields.Boolean(
        compute='_compute_is_inspection_question')

    @api.depends('question')
    def _compute_is_inspection_question(self):
        for rec in self:
            if re.match(r'.*(please complete).*(in fastfield)', rec.question, flags=re.IGNORECASE):
                rec.is_inspection_question = True
            else:
                rec.is_inspection_question = False

    def _get_survey(self):
        self.ensure_one()
        if not self.is_inspection_question:
            return
        survey_title = re.sub(
            r'(?:please complete | in fastfield)', "", self.question, flags=re.IGNORECASE)
        survey = self.env['survey.survey'].get_survey_by_title(survey_title)
        return survey

    def get_survey(self):
        self.ensure_one()
        survey = self._get_survey()
        if not survey:
            raise UserError(
                _('The survey belong to this inspection question is not exist. Please contact to Administrator to create it.'))
        return survey
