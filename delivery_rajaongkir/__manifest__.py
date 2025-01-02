# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Rajaongkir - Delivery Costs",
    'description': "Ongkos Kirim JNE, POS, TIKI, dll menggunakan RajaOngkir.com",
	'author': "Tarkiz.Biz",
    'category': 'Warehouse',
    'version': '1.0',
    'depends': ['delivery', 'mail', 'website', 'website_sale', 'contacts','stock', 'website_sale_delivery'],
    'data': [
        # 'views/web_asset.xml',
        "security/ir.model.access.csv",
        'views/delivery_rajaongkir_view.xml',
        'views/stock_report_deliveryslip.xml',
        'views/website_sale_templates.xml',
    	# 'views/website_sale_petunjuk_ongkir.xml',
	    'views/website_choose_delivery.xml',
        'data/delivery_rajaongkir_data.xml',
        'data/ir_cron_data.xml',
    ],
    'external_dependencies': {'python':['simplejson']},
}


# Not Tested :  wahana, cahaya, SAP
