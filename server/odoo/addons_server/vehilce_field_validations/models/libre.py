"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError


class Libre(models.Model):
  
    _inherit="vehicle.libre"
    
    _description="This class will add field validation for vehicle"  
    
  
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    def validate_phone(self, phone_number):
        plus_found = False
        counter = 0
        for record in self:  
            
            for st in phone_number:
                print(st.isdigit())
                if  not st.isdigit():
                    if str(st) != '+':
                        raise UserError(_("You Can not Have Characters in a mobile Number except '+'"))
                    if str(st) == '+' and plus_found == True:
                        raise UserError(_("You Can not use multilple '+' in phone number"))
                    if str(st) == '+' and plus_found == False:
                        plus_found = True
                    if str(st) == '+' and counter != 0:
                       raise UserError(_("Invalid position of '+' in phone number"))
                if st.isdigit():
                    print('st', st)
        
                    if phone_number[0] != '0':
                        if str(phone_number[0]) != '+':
                            raise UserError(_("A Valid mobile Number Starts With 0 or +"))
                    if len(phone_number) != 10:
                        if len(phone_number) != 13:
                            raise UserError(_("A Valid mobile Number Has 10 Digits"))
                counter+=1

    
    @api.onchange("total_weight")
    def on_change_total_weight(self):
        self.validate_integer(self.total_weight,(_("Total weight")))
       
    
    @api.onchange("items_weight")
    def on_change_items_weight(self):
        self.validate_integer(self.items_weight,(_("Single weight")))
       
    
    @api.onchange("cylinder_amount")
    def on_change_cylinder_amount(self):
        self.validate_integer(self.cylinder_amount,(_("Cylinder amount")))
       
       
    @api.onchange("phone_number")
    def on_change_phone_number(self):
        self.validate_phone(self.phone_number)
        
    
    
  
   