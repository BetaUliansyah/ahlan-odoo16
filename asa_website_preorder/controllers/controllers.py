# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """super the function to add new button in the home portal"""
        values = super()._prepare_home_portal_values(counters)
        if 'pre_order_count' in counters:
            current_user = request.env['res.users'].sudo().browse(
                request.env.uid)
            # pre_order_count = request.env['pre.order'].search_count([('partner_id', '=', current_user.partner_id.id)])

            cr = request.env.cr
            cr.execute(
                                """
                                    SELECT p.product_id, sum(p.product_qty) as total FROM pre_order p
                                    WHERE p.partner_id = %s GROUP BY p.product_id
                                """
                                % (current_user.partner_id.id)
                            )

            preorder = cr.dictfetchall()



            values['pre_order_count'] = len(preorder)
        return values

    @http.route(['/my/pre_order'], type='http', auth="user", website=True)
    def portal_my_pre_order(self, **kwargs):
        current_user = request.env['res.users'].sudo().browse(request.env.uid)
        # pre_order = request.env['pre.order'].sudo().search(
        #     [('partner_id', '=', current_user.partner_id.id)])

        cr = request.env.cr
        cr.execute(
                            """
                                SELECT p.product_id, sum(p.product_qty) as total FROM pre_order p
                                WHERE p.partner_id = %s GROUP BY p.product_id
                            """
                            % (current_user.partner_id.id)
                        )

        preorder = cr.dictfetchall()

        data = []
        for rec in preorder:
            product_id = rec['product_id']
            product  = request.env['product.product'].search([('id','=',product_id)])
            total = rec['total']


            cr.execute(
                            """
                                SELECT ml.product_id, sum(ml.quantity) as qty_inv FROM account_move_line ml
                                JOIN  account_move am ON am.id = ml.move_id
                                WHERE am.partner_id = %s and ml.product_id = %s and move_type = 'out_invoice' and am.payment_state = 'paid' GROUP BY ml.product_id
                            """
                            % (current_user.partner_id.id, product_id)
                        )

            invoice = cr.dictfetchall()
            print ("=================invoice==============", invoice)
            if not invoice or invoice[0] == None:
                qty_inv = 0
            else :
                for inv in invoice :
                    qty_inv = inv['qty_inv']

            print ("=================qty==============", qty_inv)

            data.append({   'product_id': product.id,
                            'product_template_id': product.product_tmpl_id.id,
                            'product_name': product.name,
                            'total': total,
                            'qty_inv': int(qty_inv),
                            'sisa': int(total - qty_inv),
                            'status': product.status_preorder
                        })


        return request.render("asa_website_preorder.portal_my_pre_order",
                              {'pre_order': data,
                               'page_name': 'pre_order'})


    @http.route(['/my/pre_order/<int:order_id>'], type='http', auth='user',
                website=True)
    def view_preorder_details(self, order_id):
        current_user = request.env['res.users'].sudo().browse(request.env.uid)
        obj_preorder = request.env['pre.order'].sudo().search(
            [('product_id', '=', order_id),('partner_id', '=', current_user.partner_id.id)])

        cr = request.env.cr
        cr.execute(
                            """
                                SELECT p.product_id, sum(p.product_qty) as total FROM pre_order p
                                WHERE p.partner_id = %s and p.product_id = %s GROUP BY p.product_id
                            """
                            % (current_user.partner_id.id, order_id)
                        )

        preorder = cr.dictfetchall()


        data = []
        for rec in preorder:
            product_id = rec['product_id']
            product  = request.env['product.product'].search([('id','=',product_id)])
            total = rec['total']


            cr.execute(
                            """
                                SELECT ml.product_id, sum(ml.quantity) as qty_inv FROM account_move_line ml
                                JOIN  account_move am ON am.id = ml.move_id
                                WHERE am.partner_id = %s and ml.product_id = %s and move_type = 'out_invoice' and am.payment_state = 'paid' GROUP BY ml.product_id
                            """
                            % (current_user.partner_id.id, product_id)
                        )

            invoice = cr.dictfetchall()
            print ("=================invoice==============", invoice)
            if not invoice or invoice[0] == None:
                qty_inv = 0
            else :
                for inv in invoice :
                    qty_inv = inv['qty_inv']


        return request.render('asa_website_preorder.website_preorder_detail',
                                {'preorder_product_id': product.id,
                                 'preorder_product_name': product.name,
                                 'preorder_total': total,
                                 'qty_inv': int(qty_inv),
                                 'sisa': int(total - qty_inv),
                                 'data_preorder' : obj_preorder,
                                 'page_name': 'preorder_details'})


    
    @http.route(['/preorder/order'], type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def preorder_update(self, product_id, qty, set_qty=0, **kw):

        request.website.sale_get_order(force_create=1)._cart_update(
            product_id=int(product_id),
            add_qty=float(qty),
            set_qty=float(set_qty)
        )
        
                    
        return request.redirect("/shop/cart")
