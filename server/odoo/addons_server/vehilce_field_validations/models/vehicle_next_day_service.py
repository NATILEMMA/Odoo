"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError


class Nextservicedays(models.Model):
  
    _inherit="next.service.days"
    
    _description="This class will add field validation for fleet.wittenoff"  
    

  
    

  
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
    @api.onchange("days")
    def on_change_cost_estimation(self):
        self.validate_integer(self.days,"days")
