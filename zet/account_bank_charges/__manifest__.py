{
    'name': "Zet Account Bank Charges",
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': """ Add Separate Journal Entries for Bank Charges in Payment""",
    'depends': ['base', 'account'],
    'data': [
        'views/account_account_views.xml',
        'views/account_journal_views.xml',
        'views/account_payment_register_views.xml'
    ],
    'license': 'LGPL-3',
    'application': False,
}
