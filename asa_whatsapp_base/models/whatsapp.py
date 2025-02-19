# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
import requests
from odoo.exceptions import UserError, ValidationError
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime


class WhatsappGroup(models.Model):
    _name = 'whatsapp.group'
    _description = "Send Message Group"
    _rec_name ="group_admin"
    
    
    group_admin = fields.Char('Group Admin Number')
    group_id = fields.Char('GroupID')
    message = fields.Text('Message')
    
    @api.onchange('group_admin')
    def Onchange_no_wa(self):
        if self.group_admin:
            no = self.group_admin[0:3]
            print ('==============no wa=============', no)
            if no != '+62' :
                mobile = self.group_admin[1:]
                no_wa = '+62'+ mobile
                self.group_admin = no_wa
                
    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text
    
    
    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
        
    def send_message_wablas(self, groupA, groupID, isi):
        kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
        if kon :
            base_url = kon.base_url
            token = kon.token
             
            groupAdmin = groupA
            groupID  = groupID
            message  = isi
             
            headers = {
                'Authorization': token
            }
             
            jsonBody = {
                'isGroup': True,
                'phone': groupID,
                'message': message
            }

            url =  base_url+"/api/send-message"
             
            r = requests.post(url, 
                headers=headers,
                data=jsonBody)
            
            kode = str(r.status_code)
            if kode == '200' :
                status = 'sent'
            else :
                status = 'fail'
                            
                            
                            
            obj_log = self.env['log.wa']
            obj_log.create({
                                'number_admin':groupAdmin,
                                'group_name': groupID,
                                'message': message,
                                'state' : status,
                                'type_send' : 'group',
                                'date_report': datetime.utcnow(),
                                'response' : str(r.content)
                            })
        else :
            print ('================tidak ada Account====================')
            #raise Warning(_("Account Wablas not Found or Not Active....!!!"))
        
    def send_wa(self):
        groupA = self.group_admin
        groupID = self.group_id
        isi = self.message
        self.send_message_wablas(groupA, groupID, isi)
            
        
    def send_message_wablas_log(self, groupA, groupID, isi):
        kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
        if kon :
            groupAdmin = groupA
            groupID  = groupID
            message  = isi
                           
                            
            obj_log = self.env['log.wa']
            log_sama = obj_log.search([('message','=', message)])
            if not log_sama :
                obj_log.create({
                                    'number_admin':groupAdmin,
                                    'group_name': groupID,
                                    'message': message,
                                    'state' : 'fail',
                                    'type_send' : 'group',
                                    'date_report': datetime.utcnow()
                                })
                
    def send_wa_log(self):
        groupA = self.group_admin
        groupID = self.group_id
        isi = self.message
        self.send_message_wablas_log(groupA, groupID, isi)
            
class WhatsapPersonal(models.Model):
    _name = 'whatsapp.personal'
    _description = "Send Message Personal"
    _rec_name ="group_admin"
    
    
    group_admin = fields.Char('Number')
    message = fields.Text('Message')
    
    @api.onchange('group_admin')
    def Onchange_no_wa(self):
        if self.group_admin:
            no = self.group_admin[0:3]
            print ('==============no wa=============', no)
            if no != '+62' :
                mobile = self.group_admin[1:]
                no_wa = '+62'+ mobile
                self.group_admin = no_wa
                
    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text
    
    
    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
        
    def send_message_personal_wablas(self, groupA, isi):
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
            print ('================tidak ada Account====================')
        
    def send_wa_personal(self):
        groupA = self.group_admin
        isi = self.message
        self.send_message_personal_wablas(groupA, isi)

            
        
    def send_message_personal_wablas_log(self, groupA, isi):
        kon = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
        if kon :
            groupAdmin = groupA
            message  = isi
                           
                            
            obj_log = self.env['log.wa']
            obj_log.create({
                                'number_admin':groupAdmin,
                                'message': message,
                                'state' : 'fail',
                                'type_send' : 'personal',
                                'date_report': datetime.utcnow()
                            })
        else :
            print ('================tidak ada Account====================')
        
    def send_wa_personal_log(self):
        groupA = self.group_admin
        isi = self.message
        self.send_message_personal_wablas_log(groupA, isi)
        
class WhatsappKonf(models.Model):
    _name = 'whatsapp.konf'
    _description = "Konfigurasi Whatsapp"
    _rec_name ="token"
    
    aktif = fields.Boolean(string="Active", default = False)
    token = fields.Char("Token")
    base_url = fields.Char("Base URL")
    
    @api.onchange('aktif')
    def active_onchange(self):
        if self.aktif == True :
            aktif = self.search([('aktif','=', True)])
            if aktif :
                return {'value':{'aktif' : False},'warning':{'title':'Peringatan','message':"Sudah ada Account yang active tidak boleh ada 2 account yang Active....!!!"}}
                
 
class MessageWhatsappTemplate(models.Model):
    _name = "asa.wa.template"
    
    name = fields.Char(required=True, string='Template Name')
    type = fields.Selection([('posted','Posted Invoice'), ('paid','Paid Invoice')],
                                   required=True, string='Type Template')
    isi_pesan = fields.Text(required=True, string='Message') 


class SoWhatsapp(models.Model):
    _name = "so.wa.template"
    
    name = fields.Char(required=True, string='Template Name')
    isi_pesan = fields.Text(required=True, string='Isi Pesan')

class DeliveryWhatsapp(models.Model):
    _name = "do.wa.template"
    
    name = fields.Char(required=True, string='Template Name')
    isi_pesan = fields.Text(required=True, string='Isi Pesan')       
        
        

        

    
    
    