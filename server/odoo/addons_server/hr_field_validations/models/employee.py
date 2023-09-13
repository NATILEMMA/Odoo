"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Employee(models.Model):
    
    _inherit="hr.employee"
    
    _description="This class will add field validation for employee"  
    
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", tracking=True, translate=False, size=9)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], groups="hr.group_hr_user", default="male", tracking=True)
    
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency contact', help='Enter here the emergency contact of the employee',
        groups="hr.group_hr_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('is_emergency','=',True)]")
    emergency_phone = fields.Char("Emergency Phone", related="emergency_contact.phone", groups="hr.group_hr_user", tracking=True, translate=False)
    
    
    @api.onchange('address_id')
    def _onchange_address(self):
            self.work_phone = self.address_id.phone
            self.mobile_phone = self.address_id.mobile
            self.work_email = self.address_id.email
            self.work_location = self.address_id.street_name
    
    @api.onchange('passport_id')
    def _onchange_passport(self):
        for rec in self:
            if(rec.passport_id):
                if not( re.match(r'^[A-Za-z][A-Za-z0-9]{8}$', rec.passport_id)):
                    raise ValidationError(_("The passport number you enter should start with a letter with size of 9 characters total!"))
                
                
        
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
    
    @api.onchange("children")
    def on_change_integer_field(self):
        self.validate_integer(self.children,(_("Children")))
        
        
        
    @api.onchange("km_home_work")
    def on_change_km_home_work(self):
        self.validate_integer(self.km_home_work,(_("Kilo meter work from home")))
        
        
    @api.onchange("pin")
    def on_change_pin(self):
        self.validate_integer(self.pin,(_("Pin")))
        
        
    
        
class ResPartnerExtended(models.Model):
    """Model res partner extended."""

    _inherit = 'res.partner'

  
    is_emergency = fields.Boolean(string='Is Emergency contact')
    
    
class ResUserExtended(models.Model):
    """Model res partner extended."""

    _inherit = ['res.users']

  
    is_emergency = fields.Boolean(string='Is Emergency contact')
    
    
    emergency_contact = fields.Many2one(related='employee_id.emergency_contact', readonly=False, related_sudo=False, translate=False)
