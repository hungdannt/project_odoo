{
    'name': 'Rope Custom Accounting',
    'summary': 'Rope Custom Accounting',
    'description': 'Rope Custom Accounting',
    'category': 'Accounting',
    'version': '15.0.0.1.7',
    'depends': ['account_reports', 'web'],
    'data': [
        'data/report_paperformat.xml',
        'data/account_move_bank_data.xml',
        'security/ir.model.access.csv',
        'security/account_move_bank_rule.xml',
        'views/report_invoice.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/account_move_bank_views.xml',
    ],
    'application': True,
}
