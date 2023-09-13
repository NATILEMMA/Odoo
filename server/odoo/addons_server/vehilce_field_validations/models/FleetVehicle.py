"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError , ValidationError


class Vehicle(models.Model):
  
    _inherit="fleet.vehicle"
    
    _description="This class will add field validation for vehicle"  
    


  
    def validate_integer(self, integer_field,field_name):
        for record in self:
            if isinstance(integer_field, float):
                if integer_field < 0.0:
                    raise ValidationError(_("The {} field must be non-negative".format(field_name)))
            else:
                if integer_field < 0:
                     raise ValidationError(_("The {} field must be non-negative".format(field_name)))
    
    @api.onchange("horsepower")
    def on_change_horsepower(self):
        self.validate_integer(self.horsepower,(_("Horse power")))
       
    
    @api.onchange("power")
    def on_change_power(self):
        self.validate_integer(self.power,(_("Power")))
       
    
    @api.onchange("cylinders")
    def on_change_cylinders(self):
        self.validate_integer(self.cylinders,(_("Cylinder")))
       
    
    @api.onchange("odometer")
    def on_change_odometer(self):
        self.validate_integer(self.odometer,(_("Odomenter")))
       
    
    @api.onchange("co2")
    def on_change_co2(self):
        self.validate_integer(self.co2,(_(" Carbon Dioxide")))
       
    
    @api.onchange("vehicle_length")
    def on_change_vehicle_length(self):
        self.validate_integer(self.vehicle_length,(_("vehcile Length")))
       
    
    @api.onchange("vehicle_width")
    def on_change_vehicle_width(self):
        self.validate_integer(self.vehicle_width,(_("vehicle width")))
       
    @api.onchange("vehicle_height")
    def on_change_vehicle_height(self):
        self.validate_integer(self.vehicle_height,(_("Vehicle height")))
       
    
    @api.onchange("seats")
    def on_change_seats(self):
        self.validate_integer(self.seats,(_("Seats")))
       
    
          
    
    @api.onchange("fuel_capacity")
    def on_change_fuel(self):
        self.validate_integer(self.fuel_capacity,(_("Feul Capacity")))
       
    
    @api.onchange("payment_deduction")
    def on_change_payment_deduction(self):
        self.validate_integer(self.payment_deduction,(_("payment deduction")))
       
    
    @api.onchange("payment")
    def on_change_payment(self):
        self.validate_integer(self.payment_deduction,(_("Payment")))
       
   