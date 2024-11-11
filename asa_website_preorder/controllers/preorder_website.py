# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import datetime
from odoo import _
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_sale.controllers.main import WebsiteSale
PPG = 20  # Products Per Page
PPR = 4   # Products Per Row
from odoo.exceptions import UserError

        
class WebsitePreorder(http.Controller):
    @http.route(['/preorder','/preorder/page/<int:page>'], type='http', auth="public", website=True)
    def preorder(self,page=1,ppg=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        values = {}
        ProductObj = request.env['product.template']
        domain = []

        domain += [('pre_order_products','=',True),("website_published", "=", True)]

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG


        product_count = ProductObj.sudo().search_count(domain)
        pager = request.website.pager(
            url="/preorder",
            total=product_count,
            page=page,
            scope=7,
            step=ppg

        )
        
        # url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post

        products = ProductObj.sudo().search(domain, limit=ppg, offset=pager['offset'])
        request.session['my_preorder_products'] = products.ids[:100]
        values.update({
            'products': products,
            'page_name': 'Pre Order Products',
            'pager': pager,
            'default_url': '/preorder',
            })
        
        return request.render("asa_website_preorder.preorder",values)
    
    @http.route(['/preorder/konfirmasi/'], type='http', auth="user", website=True)
    def konfirmasi_preorder(self, product_id, **post):
        product = request.env['product.template'].sudo().search([('id', '=', product_id)])
        partner = request.env.user.partner_id
 
        return request.render("asa_website_preorder.preorder_confirmation", {
            'product' : product,
            'partner' : partner,
            'valid' : True,
            })
        
    @http.route(['/preorder/confirmation/submit'], type='http', auth="user", methods=['GET', 'POST'], website=True, csrf=False)
    def preorder_confirmation_submit(self, **post):
        product = post.get('product_id')
        product_template = request.env['product.template'].sudo().search([('id', '=', int(post.get('product_id')))])
        product_product =request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(post.get('product_id')))])
        partner = request.env.user.partner_id
        print ("===============salda preorder=============", post.get('qty_preorder'), post.get('saldo_preorder'))
        
        if int(post.get('qty_preorder')) > int(post.get('saldo_preorder')):
            print ("===============if=============", post.get('qty_preorder'))
            return request.render("asa_website_preorder.preorder_confirmation", {
            'product' : product_template,
            'partner' : partner,
            'valid' : False,
            })

        else :
            print ("===============Else=============", post.get('qty_preorder'))

            data = {
                'partner_id'       : int(post.get('partner')),
                'product_id'       : int(product_product),
                'pre_product_id'   : int(post.get('product_id')),
                'product_qty'      : post.get('qty_preorder')
            }
            
            

            request.env['pre.order'].sudo().create(data)
            return request.render("asa_website_preorder.preorder_thankyou", {'product': product})


    @http.route('/update/qty/edit', type='json', auth="public",
                website=False, csrf=False, methods=['GET', 'POST'])
    def update_qty_order(self, **post):
        """Update the cancellation reason and state of a sale order to
          'cancel'."""

        print ("=====================product==========", post.get('order_id'), post.get('qty'))
        sale_order_id = request.env['pre.order'].sudo().browse(int(post.get('order_id')))
        sale_order_id.write({
                                'product_qty'       : post.get('qty')
                            })
        return sale_order_id


    @http.route('/create_cancel_order', type='json', auth="public",
                website=False, csrf=False, methods=['GET', 'POST'])
    def update_qty_order(self, **post):
        """Update the cancellation reason and state of a sale order to
          'cancel'."""

        product  = request.env['product.product'].search([('id','=',post.get('product'))])
        current_user = request.env['res.users'].sudo().browse(request.env.uid)

        data = {
                    'partner_id'    : current_user.partner_id.id,
                    'product_id'    : int(post.get('product')),
                    'product_qty'   : int(post.get('qty')),
                    'note'          : post.get('note')
                }

        cancel_order = request.env['cancel.pre.order'].sudo().create(data)
        return cancel_order
