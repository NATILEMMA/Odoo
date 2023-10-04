"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Expence(models.Model):
  
    _inherit= "hr.expense"
    
    _description="This class will add field validation for hr expence"  
    

  
  
  
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
  
    
    @api.onchange("unit_amount")
    def on_change_unit_amount(self):
        self.validate_integer(self.unit_amount,(_("Unit amount")))
        
    
    @api.onchange("quantity")
    def on_change_quantity(self):
        self.validate_integer(self.quantity,(_("Quantity")))
        
    
