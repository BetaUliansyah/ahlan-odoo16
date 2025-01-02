# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

#     def _get_delivery_methods(self):
#         res = super(SaleOrder, self)._get_delivery_methods()
# #         address = self.partner_shipping_id
# #         # searching on website_published will also search for available website (_search method on computed field)
# #         delivery = self.env['delivery.carrier'].sudo().search([('website_published', '=', True)]).available_carriers(address)
#         delivery = res
#         layanan = []
#         for d in delivery :
#             carrier = self.env['delivery.carrier'].sudo().browse(d.id)
#             rate = carrier.rate_shipment(self)
#             if rate.get('success'):
#                 if rate['price'] != -1:
#                     layanan.append(d.id)
# 
#         list_layanan = layanan
#         deliver_ongkir =  self.env['delivery.carrier'].sudo().search([('id' ,'in', list_layanan)])          
#         return deliver_ongkir

    def _check_carrier_quotation(self, force_carrier_id=None):
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']

        if self.only_services:
            self.write({'carrier_id': None})
            self._remove_delivery_line()
            return True
        else:
            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id

            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            available_carriers = self._get_delivery_methods()
            if carrier:
                if carrier not in available_carriers:
                    carrier = DeliveryCarrier
                else:
                    # set the forced carrier at the beginning of the list to be verfied first below
                    available_carriers -= carrier
                    available_carriers = carrier + available_carriers
            if force_carrier_id or not carrier or carrier not in available_carriers:
                for delivery in available_carriers:
                    verified_carrier = delivery._match_address(self.partner_shipping_id)
                    if verified_carrier:
                        carrier = delivery
                        break
                self.write({'carrier_id': carrier.id})
            self._remove_delivery_line()
            if carrier:
                res = carrier.rate_shipment(self)
                if res.get('success'):
                    if res['price'] == -1 :
                        raise ValidationError('Maaf Layanan tidak Tersedia' )
                    else : 
                        self.set_delivery_line(carrier, res['price'])
                        self.delivery_rating_success = True
                        self.delivery_message = res['warning_message']
                else:
                    self.set_delivery_line(carrier, 0.0)
                    self.delivery_rating_success = False
                    self.delivery_message = res['error_message']

        return bool(carrier)
