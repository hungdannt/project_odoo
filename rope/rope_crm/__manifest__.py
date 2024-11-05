# -*- coding: utf-8 -*-

{
    'name': 'Rope CRM',
    'version': '15.0.0.0.3',
    'category': 'Marketing/CRM',
    'website': '',
    'description': "",
    'depends': ['crm'],
    'data': [
        'security/crm_lead_security.xml',
        'security/res_partner_security.xml',
        'security/ir.model.access.csv',
        'security/crm_stage_security.xml',

        'views/crm_stage_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
