# -*- coding: utf-8 -*-
{
    'name': 'OnSite Companion Base Fastapi',
    'version': '17.0.1.1.27',
    'summary': 'Extend features of base_fastapi module',
    'author': 'H&M Technology Pty Ltd',
    'description': """
    This module extends features of base_fastapi module and adds the new apis for system.
    Note: Set debug = False in the config file in the production environment.
    """,
    'license': 'LGPL-3',
    'depends': ['haverton_base'],
    'data': [
        'data/fastapi_endpoint_data.xml',
        'views/res_config_settings_views.xml',
        'views/ir_model_fields_views.xml',
    ],
    'installable': True,
    'application': True,
}
