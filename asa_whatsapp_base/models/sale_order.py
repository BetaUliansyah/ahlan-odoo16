from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
import requests

class SaleOrder(models.Model):
	_inherit = 'sale.order'


	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		self.send_message_personal_wablas()
		return res


	def set_template(self, isi):
		carier = self.env['sale.order.line'].search([('order_id', '=', self.id),('is_delivery', '=',True)],limit=1)
		if carier :
			delivery = str(carier.name)
		else :
			delivery = 'Tidak Ada'

		amount = self.amount_total
		thousands_separator = "."
		fractional_separator = ","

		currency = "Rp {:,.2f}".format(amount)

		if thousands_separator == ".":
			main_currency, fractional_currency = currency.split(".")[0], currency.split(".")[1]
			new_main_currency = main_currency.replace(",", ".")
			currency = new_main_currency + fractional_separator + fractional_currency
		
		#formatted_float = "Rp {:.,2f}".format(self.amount_total)

		print ("========format=========", currency)

		res = isi.replace('{delivery}', delivery)
		res = res.replace('{customer}', self.partner_id.name or '')
		res = res.replace('{so}', self.name or '')
		res = res.replace('{amount}', str(currency) or '')
		return res  
	
	def send_message_personal_wablas(self):
		if not self.partner_id.mobile:
			raise Warning("Mobile Number Customer is empty")
		else :
			kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
			if kon :
				token = kon.token
				base_url = kon.base_url

				template = self.env['so.wa.template'].search([],limit=1)  
				isi = template.isi_pesan  
				pesan = self.set_template(isi)
				 
				number = self.partner_id.mobile
				message  = pesan
				 
				headers = {
					'Authorization': token
				}
				 
				jsonBody = {
					'phone': number,
					'message': message
				}

				url =  base_url+"/api/send-message"
				 
				r = requests.post(url, 
					headers=headers,
					data=jsonBody)

				print ("================request=================", r)
				
				kode = str(r.status_code)
				if kode == '200' :
					status = 'sent'
				else :
					status = 'fail'
								
								
								
				obj_log = self.env['log.wa']

				obj_log.create({
									'number_admin':number,
									'message': message,
									'state' : status,
									'type_send' : 'personal',
									'date_report': datetime.utcnow(),
									'response' : str(r.content)
								})
			else :
				raise Warning("Belum ada Konfigurasi Account WhatsApp")



class StockPicking(models.Model):
	_inherit = 'stock.picking'


	# def action_confirm(self):
	#     res = super(SaleOrder, self).action_confirm()
	#     self.send_message_personal_wablas()
	#     return res


	status_whatsapp  = fields.Selection([   ('sent', 'Delivered'),
											('new', 'New')
											], default="new", string='Status Whatsapp', readonly=True)


	def set_template(self, isi):
		delivery = str(self.carrier_id.name)

		res = isi.replace('{delivery}', delivery)
		res = res.replace('{customer}', self.partner_id.name or '')
		res = res.replace('{noresi}', self.carrier_tracking_ref or '')
		return res  

	# def cron_wablas(self):
	#   delivery = self.search([('state', '=', 'assigned'),('carrier_tracking_ref', '!=', False),('partner_id', '!=', False),
	#       ('picking_type_id.code', '=', 'outgoing')])
	#   if delivery :
	#       for d in delivery:
	#           for mv in d.move_ids_without_package:
	#               mv.quantity_done = mv.product_uom_qty
	#           d.button_validate()
	#           print ("============validate==========")
	#           if d.status_whatsapp != 'sent' :
	#               if not d.partner_id.mobile:
	#                   return
	#               else :
	#                   kon = self.env['whatsapp.konf'].search([],limit=1)
	#                   if kon :
	#                       token = kon.name

	#                       template = self.env['do.wa.template'].search([],limit=1)  
	#                       isi = template.isi_pesan  
	#                       pesan = d.set_template(isi)
							 
	#                       number = d.partner_id.mobile
	#                       message  = pesan
							 
	#                       headers = {
	#                           'Authorization': token
	#                       }
							 
	#                       jsonBody = {
	#                           'phone': number,
	#                           'message': message
	#                       }
							 
	#                       r = requests.post("https://jogja.wablas.com/api/send-message", 
	#                           headers=headers,
	#                           data=jsonBody)

	#                       print ("================request=================", r)
							
	#                       kode = str(r.status_code)
	#                       if kode == '200' :
	#                           status = 'sent'
	#                       else :
	#                           status = 'fail'
											
											
											
	#                       obj_log = self.env['log.wa']
	#                       obj_log.create({
	#                                           'name':number,
	#                                           'message': message,
	#                                           'state' : status,
	#                                           'date': fields.Datetime.now(),
	#                                           'response' : str(r.content)
	#                                       })
							
	#                       d.status_whatsapp = 'sent'

	#                   else :
	#                       raise Warning("Belum ada Konfigurasi Token Whatsapp...!!")
	
	# def send_message_personal_wablas(self):
	#   if not self.partner_id.mobile:
	#       raise Warning("Mobile Number Customer is empty")
	#   else :
	#       kon = self.env['whatsapp.konf'].search([],limit=1)
	#       if kon :
	#           token = kon.name

	#           template = self.env['do.wa.template'].search([],limit=1)  
	#           isi = template.isi_pesan  
	#           pesan = self.set_template(isi)
				 
	#           number = self.partner_id.mobile
	#           message  = pesan
				 
	#           headers = {
	#               'Authorization': token
	#           }
				 
	#           jsonBody = {
	#               'phone': number,
	#               'message': message
	#           }
				 
	#           r = requests.post("https://jogja.wablas.com/api/send-message", 
	#               headers=headers,
	#               data=jsonBody)

	#           print ("================request=================", r)
				
	#           kode = str(r.status_code)
	#           if kode == '200' :
	#               status = 'sent'
	#           else :
	#               status = 'fail'
								
								
								
	#           obj_log = self.env['log.wa']
	#           obj_log.create({
	#                               'name':number,
	#                               'message': message,
	#                               'state' : status,
	#                               'date': fields.Datetime.now(),
	#                               'response' : str(r.content)
	#                           })
				
	#           self.status_whatsapp = 'sent'

	#       else :
	#           raise Warning("Belum ada Konfigurasi Token Whatsapp...!!")

# class KonfirmasiPembayaran(models.Model):
#   _inherit = 'konfirmasi.pembayaran'


#   # def action_confirm(self):
#   #     res = super(SaleOrder, self).action_confirm()
#   #     self.send_message_personal_wablas()
#   #     return res


#   def set_template(self, isi):

#       amount = self.amount
#       thousands_separator = "."
#       fractional_separator = ","

#       currency = "Rp {:,.2f}".format(amount)

#       if thousands_separator == ".":
#           main_currency, fractional_currency = currency.split(".")[0], currency.split(".")[1]
#           new_main_currency = main_currency.replace(",", ".")
#           currency = new_main_currency + fractional_separator + fractional_currency
		
#       #formatted_float = "Rp {:.,2f}".format(self.amount_total)

#       print ("========format=========", currency)

#       res = isi.replace('{customer}', self.partner_id.name or '')
#       res = res.replace('{so}', self.referensi or '')
#       res = res.replace('{amount}', str(currency) or '')
#       return res  
	
#   def send_message_personal_wablas(self):
#       if not self.partner_id.mobile:
#           raise Warning("Mobile Number Customer is empty")
#       else :
#           kon = self.env['whatsapp.konf'].search([],limit=1)
#           if kon :
#               token = kon.name

#               template = self.env['konfirmasi.so.wa.template'].search([],limit=1)  
#               isi = template.isi_pesan  
#               pesan = self.set_template(isi)
				 
#               number = self.partner_id.mobile
#               message  = pesan
				 
#               headers = {
#                   'Authorization': token
#               }
				 
#               jsonBody = {
#                   'phone': number,
#                   'message': message
#               }
				 
#               r = requests.post("https://jogja.wablas.com/api/send-message", 
#                   headers=headers,
#                   data=jsonBody)

#               print ("================request=================", r)
				
#               kode = str(r.status_code)
#               if kode == '200' :
#                   status = 'sent'
#               else :
#                   status = 'fail'
								
								
								
#               obj_log = self.env['log.wa']
#               obj_log.create({
#                                   'name':number,
#                                   'message': message,
#                                   'state' : status,
#                                   'date': fields.Datetime.now(),
#                                   'response' : str(r.content)
#                               })
#           else :
#               raise Warning("Belum ada Konfigurasi Token Whatsapp...!!")