"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Advance(models.Model):
  
    _inherit= "hr.leave"
    
    _description="This class will add field validation for hr leave"  
    

  
  
  
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
  
    
    @api.onchange("number_of_days")
    def on_change_loan_amount(self):
        self.validate_integer(self.number_of_days,(_("Number of days")))
        
    

class leaveAllocation(models.Model):
  
    _inherit= "hr.leave.allocation"
    
    _description="This class will add field validation for hr leave allocations"  
    

  
  
  
  
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
  
  
    @api.onchange("number_of_days_display")
    def on_change_loan_amount(self):
        self.validate_integer(self.number_of_days_display,(_("number of days display")))
        
    
    
  