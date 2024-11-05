
{
    'name': "Zet Account Bank Charges In Payment",
    'version': '17.0.1.0.1',
    'category': 'Accounting',
    'summary': """This Module Allows to Add Separate Journal Entries for Bank Charges in Payment""",
    'description': """This Module Allows to Add Separate Journal Entries for Bank Charges in Payment""",
    'depends': ['account_bank_charges'],
    'data': [
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
