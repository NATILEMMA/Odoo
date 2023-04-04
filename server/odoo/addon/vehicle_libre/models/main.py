from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search

from odoo import api, fields, models,  SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.tools import float_is_zero, OrderedSet
from datetime import timedelta
from datetime import datetime , time
# from multiprocessing import Process
import logging
_logger = logging.getLogger(__name__)

class Vehicle_fleet_libre(models.Model):
    _inherit="fleet.vehicle"

    vehicle_libre_count = fields.Integer(
        compute="_compute_vehicle_libre_count", string="Libre Count")

    def _compute_vehicle_libre_count(self):
        obj = self.env['vehicle.libre']
        for serv in self:
            _logger.info("Helooooooooooooooooooooooooooooooooooo")
            _logger.info(serv[0])
            _logger.info(serv.id)
            _logger.info(obj.vehicle_id)
            obj_fleet = self.env['vehicle.libre'].search([('vehicle_id','=',serv.id)])
            if obj_fleet:
                serv.vehicle_libre_count = obj.search_count([('vehicle_id','=',serv.id)])
            else:
                serv.vehicle_libre_count=0

class Vehicle_libre(models.Model):
    _name = "vehicle.libre"
    _description = "Vehicle Libre"
    _inherit = 'mail.thread'


    first_name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string="User")

    # name = fields.Char(
    #     'Reference', default='/',
    #     copy=False, index=True , readonly=True)
    note = fields.Text('Notes')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    nationality=fields.Char("Nationality")
    region=fields.Char("Region")
    city=fields.Char("City")
    subcity=fields.Char("Sub City")
    woreda=fields.Char("Woreda")
    house_number=fields.Char("House Number")
    phone_number=fields.Char("Phone Number")
    plate_number=fields.Char("Plate Number")
    previous_plate_number= fields.Char("Previous Plate Number")

    vehicle_id=fields.Many2one('fleet.vehicle',string='Vehicle')
    vehicle_type=fields.Many2one('vehicle.type', string='Vehicle Type')

    made_in=fields.Char("Made In")
    vehicle_model = fields.Many2one('fleet.vehicle.model', string='Vehicle Model')

    creattion_date = fields.Datetime('Creation Date')
    chassis_number=fields.Char('Chassis Number')
    motor_number =fields.Char('Motor Number')
    parts_type = fields.Char("Parts Type")
    color=fields.Many2one('color.color', string='Color')
    fuel_type= fields.Char("Fuel Type")
    engine_horse_power = fields.Char("Engine Horse Power")
    total_weight=fields.Char("Total Weight")
    items_weight=fields.Char('Single Weight')
    cc=fields.Char("CC")
    slender_amount=fields.Char("Number of Slenders")
    allowed_work_type=fields.Char("Allowed Services Type")


