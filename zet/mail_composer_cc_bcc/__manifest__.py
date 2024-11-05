
{
    "name": "Email CC and BCC",
    "summary": "This module enables sending mail to CC and BCC partners in mail composer form.",
    "version": "17.0.2.0.0",
    "development_status": "Alpha",
    "category": "Social",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "mail",
    ],
    "data": [
        "views/res_company_views.xml",
        "views/mail_mail_views.xml",
        "views/mail_message_views.xml",
        "views/mail_template_views.xml",
        "wizards/mail_compose_message_view.xml",
    ],
}
