# -*- coding: utf-8 -*-
{
    "name": "Whatsapp Base - Using Wablas Api",
    "version": "1.01",
    "author": "Ifoel Arbeis",
    'images': ['static/description/icon.png'],
    "license": "",
    "category": "Custom",
    "summary": "Send Message to Whatsapp",
    "website": "",
    "depends": ["base","account","sale"],
    "data": [
        'data/cron.xml',
        'security/ir.model.access.csv',
        'views/whatsapp_view.xml',
        'views/whatsapp_personal_view.xml',
        'views/konfig_view.xml',
        'views/log_wa_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
