# -*- coding: utf-8 -*-
{
    'name': 'OnSite Companion Sync Companion Data',
    'version': '17.0.1.1.39',
    'summary': 'OnSite Companion Sync Companion Data Module',
    'author': 'H&M Technology Pty Ltd',
    'description': """
    Used to sync data from Companion SQL Server to Odoo.
    Require: Server must be installed the Microsoft ODBC driver for SQL Server (Linux) before.
        See: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16
    """,
    'license': 'LGPL-3',
    'depends': ['haverton_job_management'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/companion_sync_log_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
}
