"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class Document(models.Model):
  
  _inherit="hr.employee.document"
  
  _description="This class will add field validation for document"  
  
  def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
  @api.onchange("before_days")
  def on_change_before_days(self):
      self.validate_integer(self.before_days,(_("before_days")))
