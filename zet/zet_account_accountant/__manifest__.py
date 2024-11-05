# -*- coding: utf-8 -*-

{
    'name': 'ZET Accounting',
    'version': '17.0.1.0.45',
    'category': 'Accounting',
    'summary': '',
    'description': """Support data entry and processing of financial transactions such as expenses, income, and other types of transactions related to the business's accounts.""",
    'website': '',
    'depends': ['zet_sale_management', 'account_accountant', 'purchase', 'analytic'],
    'data': [
        'security/ir.model.access.csv', 
        'views/ir_attachment_views.xml',
        'views/account_move_views.xml', 
        'views/report_templates.xml',
        'views/purchase_order_views.xml',
        'views/cost_classification_type_views.xml',
        'views/account_payment_register_views.xml',
        'views/account_payment_views.xml',
        'views/account_analytic_line_views.xml',
    ],
   'assets': {
        'web.assets_backend': [
            'zet_account_accountant/static/src/**/*',
        ],
    },
    'application': False,
    'license': 'LGPL-3',
}
