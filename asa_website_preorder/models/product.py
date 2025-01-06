# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime

class ProductTemplate(models.Model):
    _inherit = "product.template"    
    
    
    pre_order_products = fields.Boolean('Pre Order Products')
    preorder_ids = fields.One2many('pre.order', 'pre_product_id', string = "Pre Order")
    tot_preorder = fields.Integer(string='Total Pre Order', store=True, readonly=True, compute='_total_preorder')
    tgl_perkiraan_ready = fields.Date(string='Tgl Perkiraan Ready')
    tgl_selesai_po = fields.Date(string='Tgl Selesai PO')
    status_preorder = fields.Selection([('open', 'Open'), 
                                     ('limit', 'Limit'),
                                     ('close', 'Closed')
                                    ], string='Status Pre Order', compute='_status_preorder')
    jml_preorder = fields.Integer(string='Jumlah Pre Order')
    saldo_preorder = fields.Integer(string='Sisa Pre Order',store=True, readonly=True, compute='_sisa_preorder')
    
    _defaults = {
        'pre_order_products' : False
    }

    @api.depends('jml_preorder','tot_preorder')
    def _sisa_preorder(self):
        for order in self:
            order.saldo_preorder = order.jml_preorder - order.tot_preorder

    
    @api.depends('preorder_ids.product_qty')
    def _total_preorder(self):
        total=0.0
        for order in self:
            if order.preorder_ids:
                for line in self.preorder_ids:
                    total+=line.product_qty
                order.tot_preorder = total
            else:
                order.tot_preorder = total
                
    @api.depends('tot_preorder', 'jml_preorder')
    def _status_preorder(self):
        for order in self:
            current_date = fields.Date.context_today(self)
            if order.tgl_selesai_po :
                if order.tgl_selesai_po < current_date:
                    order.status_preorder = "close"
                else :
                    if order.jml_preorder > 0 :
                        if order.tot_preorder >= order.jml_preorder :
                            order.status_preorder = "limit"
                        else :
                            order.status_preorder = "open"
                    else :
                        order.status_preorder = "open"
            else :
                order.status_preorder = "open"
                
                
    def cron_update_preorder(self):
        date_now = date.today().strftime('%Y-%m-%d')
        product_po = self.search([('pre_order_products', '=', True), ('tgl_selesai_po', '<', date_now)])
        for p in product_po:
            p.write({'pre_order_products': False})
        
                
class Website(models.Model):
    _inherit = 'website'
    
    def sale_product_domain(self):
        return [("sale_ok", "=", True),("pre_order_products", "!=", True)] + self.get_current_website().website_domain()
      
        
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        sisa = 0
        cr = self.env.cr
        cr.execute(
                            """
                                SELECT p.product_id, sum(p.product_qty) as total FROM pre_order p
                                WHERE p.partner_id = %s GROUP BY p.product_id
                            """
                            % (self.partner_id.id)
                        )

        preorder = cr.dictfetchall()

        data = []
        for rec in preorder:
            product_id = rec['product_id']
            product  = self.env['product.product'].search([('id','=',product_id)])
            total = rec['total']


            cr.execute(
                            """
                                SELECT ml.product_id, sum(ml.quantity) as qty_inv FROM account_move_line ml
                                JOIN  account_move am ON am.id = ml.move_id
                                WHERE am.partner_id = %s and ml.product_id = %s and move_type = 'out_invoice' and am.payment_state = 'paid' GROUP BY ml.product_id
                            """
                            % (self.partner_id.id, product_id)
                        )

            invoice = cr.dictfetchall()
            if not invoice or invoice[0] == None:
                qty_inv = 0
            else :
                for inv in invoice :
                    qty_inv = inv['qty_inv']

        sisa = int(total - qty_inv)


        try:
            if add_qty:
                add_qty = int(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = int(set_qty)
        except ValueError:
            set_qty = 0
        product = self.env['product.product'].browse(product_id)
        order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]
        warning = ''
        if product.pre_order_products :
            if set_qty and set_qty > 0 and sisa:
                qty_total = sisa
                if set_qty >= qty_total :
                    warning = _('Product Order Anda hanya tersisa %s untuk bisa ditambahkan di order') % (sisa)
                    set_qty = sisa
                    order_line.write({'product_uom_qty': sisa})

        res = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        res['warning'] = warning
        return res
