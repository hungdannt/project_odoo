# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 Alexandre Díaz
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Home customize",
    "summary": "Responsive web client, community-supported",
    "version": "15.0.0.0.1",
    "category": "Website",
    "website": "https://github.com/OCA/web",
    "author": "LasLabs, Tecnativa, Alexandre Díaz, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'web_enterprise', 'sale', 'crm', 'mail', 'contacts', 'account_accountant', 'calendar'
    ],
    "data": [
        'views/menu_item.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/rope_home_customize/static/src/scss/background.scss'
        ]
    }
}
