{
    "name": "Onsite Companion Favicon & Title",
    "version": "17.0.1.0.1",
    "author": "H&M Technology Pty Ltd,",
    'summary': 'Onsite Companion Favicon & Title Module',
    "description": "Allows to set a custom shortcut icon and title in the web browser",
    "license": "LGPL-3",
    "depends": [
        "web",
    ],
    "assets": {
        "web.assets_backend": [
            "haverton_web_favicon/static/src/js/title.js",
        ],
    },
    "data": [
            "data/res_company_data.xml",
            "views/res_company_views.xml", 
            "views/layout.xml"
            ],
    "installable": True,
}
