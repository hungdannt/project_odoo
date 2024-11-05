# -*- coding: utf-8 -*-

{
    'name': 'ZET Email',
    'version': '17.0.1.0.4',
    'category': 'Hidden',
    'summary': 'Enhanced Reply-to Functionality in Charters',
    'description': """
        Adds the functionality to set a 'Reply-to' email address in charters.
    """,
    'depends': ['mail'],
    'assets': {
        'web.assets_backend': [
            'zet_mail/static/src/**/*'
        ],
    },
    'license': 'LGPL-3',
}
