from odoo import _, api, fields, models, tools
import time
import requests
import base64
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)
MAX_RETRY = 3

class LogWa(models.Model):
    _name = 'log.wa'
    _description = "Log WhatsApp"
    _rec_name ="state"
    
    
    number_admin = fields.Char('Number')
    group_name = fields.Char('Group Name/ID')
    message = fields.Text('Message')
    state = fields.Selection([
        ('sent', 'Delivered'),
        ('fail', 'Failled')
        ], string='Status Whatsapp', readonly=True)
    type_send = fields.Selection([
        ('group', 'Group'), ('personal', 'Personal')], string='Type Send')
    date_report = fields.Datetime('Date')
    response = fields.Char('Response')
    
    
    def send_wa_log(self):
        kon_wablas = self.env['whatsapp.konf'].search([('aktif','=', True)],limit=1)
        if kon_wablas :
            token = kon_wablas.token
            base_url = kon_wablas.base_url  
            url =  base_url+"/api/send-message" 
            for log in self.search([('state','=','fail'),
                                    ('date_report','<',time.strftime('%Y-%m-%d %H:%M:%S'))]):
                if log.type_send == 'group' :
                    groupAdmin = log.number_admin
                    groupName = log.group_name
                    message = log.message
                     
                    headers = {
                                    'Authorization': token
                                }
                               
                    jsonBody = {
                                    'phone': groupAdmin,
                                    'groupId': groupName,
                                    'message': message
                                }

                    
                               
                    r = requests.post(url, 
                                              headers=headers,
                                              data=jsonBody)
                            
                    kode = str(r.status_code)
                    if kode == '200' :
                        status = 'sent'
                    else :
                        status = 'fail'
                            
                    log.write({'state':status, 'response':str(r.content) })
                    
            
                    
                elif log.type_send == 'personal' :
                    groupAdmin = log.number_admin
                    message = log.message
                     
                    headers = {
                                    'Authorization': token
                                }
                               
                    jsonBody = {
                                    'phone': groupAdmin,
                                    'message': message
                                }
                               
                    r = requests.post(url, 
                                              headers=headers,
                                              data=jsonBody)
                            
                    kode = str(r.status_code)
                    if kode == '200' :
                        status = 'sent'
                    else :
                        status = 'fail'
                            
                    log.write({'state':status, 'response':str(r.content) })
                    
                else :
                    print ('====================tdk ada type===================')
                
                
                
             
        
            
            
            