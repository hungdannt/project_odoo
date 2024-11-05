{
    'name': 'Rope Custom Employee',
    'summary': 'Rope Custom Employee',
    'description': 'Enhanced access control for the Employee module',
    'category': 'Custom',
    'version': '15.0.0.0.1',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/res_users.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
