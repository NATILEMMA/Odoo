"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError
import re 

class loan(models.Model):
  
  _inherit="hr.loan"
  
  _description="This class will add field validation for document"  
  

  
  
  
  def validate_integer(self, integer_field):
      for record in self:
          if isinstance(integer_field, float):
              if integer_field < 0.0:
                  raise ValidationError(_("The field must be non-negative"))
          else:
              if integer_field < 0:
                  raise ValidationError(_("The field must be non-negative"))

    
  
  @api.onchange("loan_amount")
  def on_change_loan_amount(self):
      self.validate_integer(self.loan_amount)

  
  @api.onchange("installment")
  def on_change_installment(self):
      for rec in self:
        self.validate_integer(self.installment)
      

class loanconfig(models.Model):
  
  _inherit="loan.advance.conf"
  
  _description="This class will add field validation for for loan config"  
  
  

  def validate_integer(self, integer_field):
      for record in self:
        
          if isinstance(integer_field, float):
              if integer_field < 0.0:
                  raise ValidationError(_("The field must be non-negative"))
          else:
              if integer_field < 0:
                  raise ValidationError(_("The field must be non-negative"))

  
  @api.onchange("percent")
  def on_change_loan_amount(self):
      for rec in self: 
        if rec.percent:
          rec.validate_integer(rec.percent)
    

 