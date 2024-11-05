# -*- coding: utf-8 -*-
{
    'name': 'OnSite Companion Inspection Management',
    'version': '17.0.1.1.84',
    'summary': 'OnSite Companion Inspection Management Module',
    'author': 'H&M Technology Pty Ltd',
    'description': """
    This module is used to manage inspection in the OnSite Companion Homes system.
    """,
    'license': 'LGPL-3',
    'depends': ['haverton_job_management'],
    'data': [
        'report/report_paperformat_data.xml',
        'report/ir_actions_report_templates.xml',
        'report/ir_actions_report.xml',
        'data/base_automation_data.xml',
        'data/survey_survey_data.xml',
        'data/mail_template_data.xml',
        'data/survey_question_rule_action_data.xml',
        'data/survey_question_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/survey_user_input_line_views.xml',
        'views/survey_question_views.xml',
        'views/survey_question_template_views.xml',
        'views/survey_survey_views.xml',
        'views/survey_user_views.xml',
        'wizard/inspection_wizard_views.xml'
    ],
    'installable': True,
    'application': True,
}
