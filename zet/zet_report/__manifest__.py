# -*- coding: utf-8 -*-

{
    'name': 'ZET Report',
    'version': '17.0.1.0.10',
    'category': 'Hidden',
    'summary': 'Integrate sales orders and account moves into detailed reports for enhanced financial tracking',
    'description': """
        This module combines sales order and account move data into comprehensive reports
    """,
    'depends': ['zet_sale_management', 'zet_account_accountant'],
    'data': [
        'views/sale_order_views.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/upload_files_wizard_views.xml',
        'reports/report_paperformat_data.xml',
        'reports/sale_order_report.xml',
        'reports/account_move_report.xml',
        'reports/report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zet_report/static/src/views/fields/**/*',
        ],
    },
    'license': 'LGPL-3',
}
