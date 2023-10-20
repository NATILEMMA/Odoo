"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError  

class Employee(models.Model):
    _inherit = 'hr.employee'

    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user,hr.group_user_custom", copy=False, translate=True)
    image_128 = fields.Image("Image 128")
    work_email = fields.Char('Work email', translate=True)
    work_phone = fields.Char('Work Phone', translate=True)
    job_title = fields.Char("Job Title", translate=True)
    hr_presence_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('to_define', 'To Define')], default='to_define')
    

  
    
    def validate_phone(self, phone_number):
        plus_found = False
        counter = 0
        for record in self:  
            
            for st in phone_number:
                print(st.isdigit())
                if  not st.isdigit():
                    if str(st) != '+':
                        raise UserError(_("You Can not Have Characters in a mobile Number except '+'"))
                    if str(st) == '+' and plus_found == True:
                        raise UserError(_("You Can not use multilple '+' in phone number"))
                    if str(st) == '+' and plus_found == False:
                        plus_found = True
                    if str(st) == '+' and counter != 0:
                       raise UserError(_("Invalid position of '+' in phone number"))
                if st.isdigit():
                    print('st', st)
        
                    if phone_number[0] != '0':
                        if str(phone_number[0]) != '+':
                            raise UserError(_("A Valid mobile Number Starts With 0 or +"))
                    if len(phone_number) != 10:
                        if len(phone_number) != 13:
                            raise UserError(_("A Valid mobile Number Has 10 Digits"))
                counter+=1
                
 
    
    @api.onchange('work_email')
    def _validate_email_address(self):
        """This function will validate the email given"""
        for record in self:
            no = ['@', '.']
            if record.work_email:
                if '@' not in record.work_email or '.' not in record.work_email:
                    raise UserError(_("A Valid Email Address has '@' and '.'"))
    
        
    @api.onchange('work_phone')
    def on_change_phone_number(self):
        self.validate_phone(self.work_phone)
    
            
    @api.onchange('mobile_phone')
    def on_change_mobile_phone(self):
        self.validate_phone(self.mobile_phone)
    
    