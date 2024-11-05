from odoo import fields, models


class CompanionSyncLog(models.Model):
    _name = 'companion.sync.log'
    _description = 'Companion SQL Statement Sync Log'

    statement = fields.Text(string="SQL Statement")
    params = fields.Text()
    multiparams = fields.Text()
    status = fields.Selection([
        ('success', 'Success'),
        ('failure', 'Failure')
    ])
    error = fields.Text(string="Failure Reason")
    user_id = fields.Many2one('res.users', string="User")

    def save_companion_sync_log_error(self, error):
        self.write({
            'status': 'failure',
            'error': str(error)
        })
