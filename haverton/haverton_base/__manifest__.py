# -*- coding: utf-8 -*-
{
    'name': 'OnSite Companion Base',
    'version': '17.0.1.1.41',
    'summary': 'OnSite Companion Base Module',
    'author': 'H&M Technology Pty Ltd',
    'description': """
    The kernel of the OnSite Companion Application.
    """,
    'license': 'LGPL-3',
    'depends': ['auth_oauth', 'base_fastapi', 'contacts'],
    'data': [
        'data/mail_message_subtype_data.xml',
        'data/auth_oauth_data.xml',
        'data/haverton_compliance_data.xml',
        'data/haverton_wr_preference_data.xml',
        'data/ir_config_parameter_data.xml',
        'security/haverton_base_groups.xml',
        'security/ir.model.access.csv',
        'views/jwt_refresh_token_views.xml',
        'views/haverton_base_menus.xml',
        'views/ir_ui_menu_views.xml',
        'views/mail_mail_views.xml',
        'views/mail_template_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml'
    ],
    'installable': True,
    'application': True,
}
