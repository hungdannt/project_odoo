{
    'name': 'Rope Backend Theme',
    'version': '15.0.1.0.1',
    'website': '',
    "depends": [
        'rope_contacts', 'crm', 'mail', 'rope_sale'
    ],
    "data": [
        'views/menu_item.xml',
        'views/ir_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "rope_backend_theme/static/src/scss/home_menu.scss",
            "rope_backend_theme/static/src/js/navbar.js",
            "rope_backend_theme/static/src/scss/*.scss",
            "rope_backend_theme/static/src/js/*.js",
        ],
        'web.assets_qweb': [
            'rope_backend_theme/static/src/webclient/home_menu/home_menu.xml',
            'rope_backend_theme/static/src/xml/*.xml',
        ],
        'web._assets_primary_variables': [
            ('replace', 'web_enterprise/static/src/legacy/scss/primary_variables.scss',
                        'rope_backend_theme/static/src/scss/primary_variables.scss'),
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
