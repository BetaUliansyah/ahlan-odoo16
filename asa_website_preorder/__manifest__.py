# -*- coding: utf-8 -*-
{
    "name": "Pre Order",
    "version": "1.01",
    "author": "Ifoel Arbeis",
    "license": "LGPL-3",
    "category": "Sales",
    "website": "",
    "depends": ["sale","website_sale","stock","product"],
    "data": [
            'security/ir.model.access.csv',
            'data/data.xml',
            'views/preorder_view.xml',
            'views/portal_preorder.xml',
            'views/product_view.xml',
            'views/website_preorder.xml'
             ],
    'assets': {
        'web.assets_frontend': [
            'asa_website_preorder/static/src/js/sale_order_portal.js'], },
    'installable': True,
    'auto_install': False,
}

