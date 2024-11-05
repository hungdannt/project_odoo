{
    'name': "Zet Purchase Team",
    'summary': """
        Manage purchase orders by purchase team and access roles
        """,
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['account', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/purchase_security.xml',
        'views/purchase_team_views.xml',
        'views/purchase_order_views.xml',
    ],
    'category': 'Inventory/Purchase',
}
