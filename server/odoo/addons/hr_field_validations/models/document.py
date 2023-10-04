"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Document(models.Model):
  
  _inherit="hr.employee.document"
  
  _description="This class will add field validation for document"  
  

  
  
  def validate_integer(self, integer_field):
    for record in self:
        if integer_field < 0:
            raise ValidationError(_("The number of days must be non-negative"))
   
  
  
  @api.onchange("before_days")
  def on_change_integer_field(self):
      self.validate_integer(self.before_days)
     
    
 