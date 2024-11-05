# -*- coding: utf-8 -*-

{
    'name': 'ZET Sales Management',
    'version': '17.0.1.0.88',
    'category': 'Sales/Sales',
    'summary': 'History Sale Managerment',
    'description': """
        Record all changes made during the sales order process, including when, by whom, and tool edits
    """,
    'website': '',
    'depends': ['sale_management'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'security/ir.model.access.csv',
        'security/sales_team_security.xml',
        'views/ir_attachment_views.xml',
        'views/product_note_views.xml',
        'views/product_pricelist_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_history_views.xml',
        'views/sale_portal_history_templates.xml',
        'views/sale_order_template_views.xml',
        'views/sale_portal_templates.xml',
        'wizard/upload_files_wizard_views.xml',
        'wizard/select_analytic_wizard_views.xml',
        'reports/sale_order_report.xml',
        'reports/sale_report_views.xml',
    ],
   
   'assets': {
        'web.assets_backend': [
            'zet_sale_management/static/src/views/fields/**/*',
            'zet_sale_management/static/src/components/**/*'
        ],
    },
    'application': False,
    'license': 'LGPL-3',
}
