# -*- coding: utf-8 -*-

{
    'name': 'ZET Purchase',
    'version': '17.0.1.0.2',
    'category': 'Inventory/Purchase',
    'summary': 'Manage purchase orders based on purchase team and roles to access',
    'description': """
        - Add group in purchase
        - Restrict user access other team documents, only access own team documents 
        - Team purchase on reporting
    """,
    'depends': ['purchase_team', 'contacts'],
    'data': [
        'security/purchase_team_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_security_views.xml', 
        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml'
    ],
    'license': 'LGPL-3',
}
