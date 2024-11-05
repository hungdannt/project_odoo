{
    'name': 'Rope Custom Contacts',
    'summary': 'Rope Custom Contacts',
    'description': 'Rope Custom Contacts',
    'category': '',
    'version': '15.0.1.0.4',
    'depends': ['contacts', 'account_followup'],
    'data': [
        'security/contacts_security.xml',
        'views/res_partner_views.xml',
        'views/contact_views.xml',
        'views/account_followup_views.xml',
        'views/partner_view.xml',
        'views/res_user_views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
}
