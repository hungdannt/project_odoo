# -*- coding: utf-8 -*-
{
    'name': 'OnSite Companion Job Management',
    'version': '17.0.1.1.135',
    'summary': 'OnSite Companion Job Management Module',
    'author': 'H&M Technology Pty Ltd',
    'description': """
    This module is used to manage jobs, activities in the OnSite Companion Homes system.
    """,
    'license': 'LGPL-3',
    'depends': ['haverton_service_provider', 'base_automation', 'mail', 'survey', 'haverton_mail_server', 'haverton_notification_management'],
    'data': [
        'data/mail_message_subtype_data.xml',
        'data/report_templates.xml',
        'data/mail_template_data.xml',
        'data/notification_template_data.xml',
        'data/base_automationd_data.xml',
        'data/ir_cron_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/mobile_filter_category_data.xml',
        'data/mobile_filter_data.xml',
        'security/project_task_security.xml',
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/base_automation_views.xml',
        'views/ir_model_fields_views.xml',
        'views/mobile_filter_views.xml',
        'views/res_config_settings_views.xml',
        'views/mobile_filter_category_views.xml',
    ],
    'installable': True,
    'application': True,
}
