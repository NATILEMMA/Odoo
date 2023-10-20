"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Employee(models.Model):
    
    _inherit="hr.employee"
    
    _description="This class will add field validation for employee"  
    
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", tracking=True, translate=False, size=9)

    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency contact', help='Enter here the emergency contact of the employee',
        groups="hr.group_hr_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('is_emergency','=',True)]")
    emergency_phone = fields.Char("Emergency Phone", related="emergency_contact.phone", groups="hr.group_hr_user", tracking=True, translate=False)
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user,hr.group_user_custom", copy=False, translate=True)
    image_128 = fields.Image("Image 128")
    work_email = fields.Char('Work email', translate=True)
    work_phone = fields.Char('Work Phone', translate=True)
    job_title = fields.Char("Job Title", translate=True)
    hr_presence_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('to_define', 'To Define')], default='to_define')
    

  
    
    @api.onchange('address_id')
    def _onchange_address(self):
            for rec in self :
                
                rec.work_phone = rec.address_id.phone
                rec.mobile_phone = rec.address_id.mobile
                rec.work_email = rec.address_id.email
                rec.work_location = rec.address_id.street_name
    
    @api.onchange('passport_id')
    def _onchange_passport(self):
        for rec in self:
            if(rec.passport_id):
                if not( re.match(r'^[A-Za-z][A-Za-z0-9]{8}$', rec.passport_id)):
                    raise ValidationError(_("The passport number you enter should start with a letter with size of 9 characters total!"))
                
                
        
    def validate_integer(self, integer_field,field_name):
        for rec in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
    
    @api.onchange("children")
    def on_change_integer_field(self):
        for rec in self :
            if rec.mobile_phone:
                rec.validate_integer(rec.children,(_("Children")))
        
        
        
    @api.onchange("km_home_work")
    def on_change_km_home_work(self):
        for rec in self :
            if rec.mobile_phone:
                rec.validate_integer(rec.km_home_work,(_("Kilo meter work from home")))
        
        
    @api.onchange("pin")
    def on_change_pin(self):
        for rec in self :
            if rec.mobile_phone:
                rec.validate_integer(rec.pin,(_("Pin")))
        
    
    def validate_phone(self, phone_number):
        plus_found = False
        counter = 0
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
        for rec in self :
            if rec.work_phone:
                rec.validate_phone(rec.work_phone)
    
            
    @api.onchange('mobile_phone')
    def on_change_mobile_phone(self):
        for rec in self :
            if rec.mobile_phone:
                rec.validate_phone(rec.mobile_phone)
    
    
        
class ResPartnerExtended(models.Model):
    """Model res partner extended."""

    _inherit = 'res.partner'

  
    is_emergency = fields.Boolean(string='Is Emergency contact')
    
    
class ResUserExtended(models.Model):
    """Model res partner extended."""

    _inherit = ['res.users']

  
    is_emergency = fields.Boolean(string='Is Emergency contact')
    
    
    emergency_contact = fields.Many2one(related='employee_id.emergency_contact', readonly=False, related_sudo=False, translate=False)
