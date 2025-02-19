from odoo import _, api, fields, models, tools
import requests
from odoo.exceptions import UserError, ValidationError
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
import base64
import json



class AccountMoveRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        res = super(AccountMoveRegister, self).action_create_payments()
        invoice = self.env['account.move'].search([('name','=', self.communication)],limit=1)
        print ("============post============", invoice)
        if invoice :
            if invoice.move_type == 'out_invoice' and invoice.payment_state == 'paid':
                if not invoice.partner_id.mobile:
                    raise ValidationError(_('Mobile Number Customer is empty'))
                else :
                    template = self.env['asa.wa.template'].search([('type','=', 'paid')],limit=1)
                    isi = template.isi_pesan
                    groupA = invoice.partner_id.mobile
                    invoice.send_message_personal_wablas(groupA, isi)
        return res





class AccountMove(models.Model):
    _inherit = "account.move"


    def attactment_report(self):
        kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
        if kon :
            token = kon.token
            base_url = kon.base_url


        # url =  base_url+"/api/send-document"

        # payload={'phone': '628156814955',
        #         'document': 'http://localhost:8010/report/pdf/sale.report_saleorder/11.pdf'}
        # files=[

        # ]
        # headers = {
        #   'Authorization': token
        # }

        # response = requests.request("POST", url, headers=headers, data=payload, files=files)

        # print(response.text)
        invoice_report = self.env.ref('account.account_invoices')
        data_record = base64.b64encode(
            self.env['ir.actions.report'].sudo()._render_qweb_pdf(
                invoice_report, [self.id], data=None)[0])
        ir_values = {
            'name': 'Invoice ' + self.name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'account.move',
        }
        invoice_report_attachment_id = self.env[
            'ir.attachment'].sudo().create(
            ir_values)
        if invoice_report_attachment_id:
            fiel_attch = self.env['ir.attachment']
            full_path = fiel_attch._full_path(invoice_report_attachment_id.store_fname)

            image_base64 = None
            with open(full_path, 'rb') as file:
                file_base64 = base64.b64encode(file.read())

            # data_attach = json.dumps(ir_values)


        headers = {
                'Authorization': token
            }


        jsonBody = {
                            'phone': self.partner_id.mobile,
                            'file': file_base64,
                            'data': data_record
                                    }

        url =  base_url+"/api/send-document-from-local"

        print ("============url=========", url)
         
        r = requests.post(url, 
            headers=headers,
            data=jsonBody)
        
        print ('================Response====================',str(r.content))



    def action_post(self):
        res = super(AccountMove, self).action_post()
        self.attactment_report()
        # if self.move_type == 'out_invoice' :  
        #     if not self.partner_id.mobile:
        #         raise ValidationError(_('Mobile Number Customer is empty'))
        #     else :
        #         template = self.env['asa.wa.template'].search([('type','=', 'posted')],limit=1)
        #         isi = template.isi_pesan
        #         groupA = self.partner_id.mobile
        #         self.send_message_personal_wablas(groupA, isi)
        return res


    def send_message_personal_wablas(self, groupA, isi):
        print ("============ok============", groupA)
        if not self.partner_id.mobile:
            raise ValidationError(_('Mobile Number Customer is empty'))
        else :
            kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
            if kon :
                token = kon.token
                base_url = kon.base_url 
                groupAdmin = groupA
                message  = isi
                 
                headers = {
                    'Authorization': token
                }
                 
                jsonBody = {
                    'phone': groupAdmin,
                    'message': message
                }

                url =  base_url+"/api/send-message"

                print ("============url=========", url)
                 
                r = requests.post(url, 
                    headers=headers,
                    data=jsonBody)
                
                print ('================Response====================',str(r.content))
                
                kode = str(r.status_code)
                if kode == '200' :
                    status = 'sent'
                else :
                    status = 'fail'
                                
                                
                                
                obj_log = self.env['log.wa']
                obj_log.create({
                                    'number_admin':groupAdmin,
                                    'message': message,
                                    'state' : status,
                                    'type_send' : 'personal',
                                    'date_report': datetime.utcnow(),
                                    'response' : str(r.content)
                                })
            else :
                raise ValidationError(_('Belum ada Konfigurasi Account WhatsApp'))