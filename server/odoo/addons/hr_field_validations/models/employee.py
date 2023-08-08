"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Employee(models.Model):
  
  _inherit="hr.employee"
  
  _description="This class will add field validation for employee"  
  


  @api.onchange("emergency_phone")
  def on_change_phone_number(self):
      if not re.match("^[0-9]{10,11}$", self.emergency_phone):
          raise ValidationError("Please enter a valid emergency phone number")
      return True
  
  
  def validate_integer(self, integer_field):
    for record in self:
        if integer_field < 0:
            raise ValidationError(_("Integer field must be non-negative"))
    return True
  
  
  @api.onchange("children")
  def on_change_integer_field(self):
      self.validate_integer(self.children)
      return True
    
    
  @api.onchange("km_home_work")
  def on_change_km_home_work(self):
      self.validate_integer(self.km_home_work)
      return True
    
  @api.onchange("pin")
  def on_change_pin(self):
      self.validate_integer(self.children)
      return True
      
  # @api.onchange("identification_id")
  # def on_change_identification_id(self):
  #     self.validate_integer(self.identification_id)
  #     return True
    
  # @api.onchange("passport_id")
  # def on_change_passport_id(self):
  #     self.validate_integer(self.passport_id)
  #     return True
    
  # @api.onchange("visa_no")
  # def on_change_visa_no(self):
  #     self.validate_integer(self.visa_no)
  #     return True
    
  # @api.onchange("permit_no")
  # def on_change_permit_no(self):
  #     self.validate_integer(self.permit_no)
  #     return True
    
  