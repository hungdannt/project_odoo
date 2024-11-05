{
    'name': "Rope Custom Sale Order",
    'summary': 'Rope Custom Sale Order',
    'description': 'Rope Custom Sale Order',
    'category': 'Custom',
    'version': '15.0.0.0.1',
    'website': '',
    'depends': ['sale','mail'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "rope_sale_order/static/src/components/message/message.scss",
        ],
    },
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
}

