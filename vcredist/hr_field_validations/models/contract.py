"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Contract(models.Model):
  
    _inherit="hr.contract"
    
    _description="This class will add field validation for contract"  
    


  
    def validate_integer(self, integer_field):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The field must be non-negative"))
            else:
                if integer_field < 0:
                    raise ValidationError(_("The field must be non-negative"))
       
    
    @api.onchange("wage")
    def on_change_wage(self):
        self.validate_integer(self.wage)
       
    
    @api.onchange("hra")
    def on_change_hra(self):
        self.validate_integer(self.hra)
       
    
    @api.onchange("da")
    def on_change_da(self):
        self.validate_integer(self.da)
       
    
    @api.onchange("travel_allowance")
    def on_change_travel_allowance(self):
        self.validate_integer(self.travel_allowance)
       
    
    @api.onchange("meal_allowance")
    def on_change_meal_allowance(self):
        self.validate_integer(self.meal_allowance)
       
    
    @api.onchange("medical_allowance")
    def on_change_medical_allowance(self):
        self.validate_integer(self.medical_allowance)
       
    
    @api.onchange("pp_contribution")
    def on_change_pp_contribution(self):
        self.validate_integer(self.pp_contribution)
       
    
    @api.onchange("other_allowance")
    def on_change_other_allowance(self):
        self.validate_integer(self.other_allowance)
       
    
   