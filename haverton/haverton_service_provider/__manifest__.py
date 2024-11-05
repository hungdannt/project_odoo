# -*- coding: utf-8 -*-
{
    'name': 'OnSite Companion Service Provider',
    'version': '17.0.1.1.25',
    'summary': 'OnSite Companion Service Provider Module',
    'author': 'H&M Technology Pty Ltd',
    'description': """
    This module is used to manage service providers which is similar to res.partner in the base module.
    """,
    'license': 'LGPL-3',
    'depends': ['haverton_base_fastapi', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/ir_model_fields_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
}
