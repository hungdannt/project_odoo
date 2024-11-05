from odoo import _, fields, models
from sqlalchemy import text
from sqlmodel import Session

from ..companion import Connection


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # companion database info
    companion_db_host = fields.Char(
        related='company_id.companion_db_host', readonly=False)
    companion_db_port = fields.Char(
        related='company_id.companion_db_port', readonly=False)
    companion_db_database = fields.Char(
        related='company_id.companion_db_database', readonly=False)
    companion_db_username = fields.Char(
        related='company_id.companion_db_username', readonly=False)
    companion_db_password = fields.Char(
        related='company_id.companion_db_password', readonly=False)

    def action_sync_companion_data(self):
        models = [
            'haverton.code',
            'haverton.work.category',
            'haverton.service.type',
            'haverton.defect.category',
            'haverton.location',
            'haverton.region',
            'haverton.address',
            'res.users',
            'res.partner',
            'haverton.service.provider.statutory.requirement',
            'project.project.stage',
            'project.project',
            'project.task',
            'haverton.service.question',
            'haverton.activity.question.answer',
            'mail.message',
        ]
        for model in models:
            self.env[model].sync_companion_data()
            self.env.cr.commit()

    def action_test_companion_connection(self):
        noti_type = 'success'
        noti_message = _("Connect successfully.")
        try:
            conn = Connection()
            engine = conn.engine
            with Session(engine) as session:
                session.execute(text("SELECT 1"))
        except Exception:
            noti_type = 'danger'
            noti_message = _("Connect failed!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                    'type': noti_type,
                    'sticky': True,
                    'message': noti_message,
            }
        }
