{
    'name': 'Rope Custom Sale',
    'summary': 'Rope Custom Sale',
    'description': 'Rope Custom Sale',
    'category': 'Custom',
    'version': '15.0.0.0.2',
    'website': '',
    'depends': ['sale_crm'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rope_sale/static/src/form_controller.js',
        ],
    },
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
}
