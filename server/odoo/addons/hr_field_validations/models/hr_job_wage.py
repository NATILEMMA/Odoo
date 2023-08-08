"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class JobSalary(models.Model):
  
  _inherit="hr.job.grade"
  
  _description="This class will add field validation for document"  
  

  
  
  
  def validate_integer(self, integer_field):
      for record in self:
          if isinstance(integer_field, float):
              if integer_field < 0.0:
                  raise ValidationError(_("The field must be non-negative"))
          else:
              if integer_field < 0:
                  raise ValidationError(_("The field must be non-negative"))
      return True
    
  
  @api.onchange("fixed_wage")
  def on_change_loan_amount(self):
      self.validate_integer(self.fixed_wage)
      return True
  
class Job(models.Model):
  
  _inherit="hr.job"
  
  _description="This class will add field validation for hr job"  
  

  
  
  
  def validate_integer(self, integer_field):
      for record in self:
          if isinstance(integer_field, float):
              if integer_field < 0.0:
                  raise ValidationError(_("The field must be non-negative"))
          else:
              if integer_field < 0:
                  raise ValidationError(_("The field must be non-negative"))
      return True
    
  
  @api.onchange("no_of_recruitment")
  def on_change_loan_amount(self):
      self.validate_integer(self.no_of_recruitment)
      return True
  
