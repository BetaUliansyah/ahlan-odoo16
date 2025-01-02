# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ongkir_real = fields.Float(
        string='Ongkir Real',
    )
    selisih_ongkir = fields.Float(
        string='Selisih Ongkir',
    )
    ongkir_so = fields.Float(
        string='Ongkir SO', compute='_compute_amount_delivery', store=True, tracking=True
    )

    @api.depends('sale_id')
    def _compute_amount_delivery(self):
        for picking in self:
            if picking.sale_id:
                picking.ongkir_so = sum(picking.sale_id.order_line.filtered('is_delivery').mapped('price_total'))

    @api.onchange('ongkir_real','ongkir_so')
    def _onchange_ongkir_real(self):
        if self.ongkir_so > 0:
            self.selisih_ongkir = self.ongkir_so - self.ongkir_real
        else:
            self.selisih_ongkir = self.ongkir_real

    def _track_rajaongkir(self):
        self.ensure_one()
        print ("\n tracking \n")
        try:
            vals = self.carrier_id.rajaongkir_get_tracking_value(self)
            print ("\n vals",vals)
            res = {
                'destination' : vals['summary']['destination'],
                'status' : vals['summary']['status'],
                'manifest' : [{
                    'code' : m['manifest_code'],
                    'description' : m['manifest_description'],
                    'date' : m['manifest_date'],
                    'time' : m['manifest_time'],
                    'city' : m['city_name'],
                } for m in vals['manifest']],
                'delivered' : vals['delivered'],
                'receiver_name' : vals['summary']['receiver_name']
            }
            print ("\n res",res)
        except:
            return False
        return res
