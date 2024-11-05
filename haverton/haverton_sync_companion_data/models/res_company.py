from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    # companion database info
    companion_db_host = fields.Char()
    companion_db_port = fields.Char()
    companion_db_database = fields.Char()
    companion_db_username = fields.Char()
    companion_db_password = fields.Char()
