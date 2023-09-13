from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import float_is_zero, OrderedSet
from datetime import timedelta
from datetime import datetime, time
# from multiprocessing import Process
import logging

_logger = logging.getLogger(__name__)

pick1 = []
pick2 = []
pick3 = []
pick4 = []



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


class MaidBy(models.Model):
    _name = 'maid.by'

    name = fields.Char(string="name", translate=True)


class LibreHistory(models.Model):
    _name = 'libre.history'

    issue_date = fields.Date(string="Inspection Date", required=True, store=True)
    notify_date = fields.Date(string="Notify Date", readonly=True, store=True)
    sticker_number = fields.Char(string="Annual Sticker Number",translate=True)
    approver = fields.Many2one('res.partner', string="Approver")
    user_id = fields.Many2one('res.users', string="User")
    rev = fields.Many2one('vehicle.libre', string="rev")


class Vehicle_fleet_libre(models.Model):
    _inherit = "fleet.vehicle"

    vehicle_libre_count = fields.Integer(
        compute="_compute_vehicle_libre_count", string="Libre Count")
    invoice_count_3 = fields.Integer(
        compute="_compute_count_invoice_3", string="expanse Count")
    invoice_count_2 = fields.Integer(
        compute="_compute_count_invoice_2", string="purchase Count")
    invoice_count_1 = fields.Integer(
        compute="_compute_count_invoice_1", string="transfer Count")

    def _compute_count_invoice_3(self):
        obj = self.env['hr.expense']
        for serv in self:
            serv.invoice_count_3 = obj.search_count([('vehicle_id', '=', self.id)])
        print("serv.invoice_count", serv.invoice_count_3)

    def _compute_count_invoice_1(self):
        obj = self.env['employee.fleet']
        for serv in self:
            serv.invoice_count_1 = obj.search_count([('fleet', '=', self.id)])
        print("serv.invoice_count", serv.invoice_count_3)

    def _compute_count_invoice_2(self):
        obj = self.env['purchase.order.line']
        for serv in self:
            serv.invoice_count_2 = obj.search_count([('vehicle_id', '=', self.id)])
        print("serv.invoice_count_2", serv.invoice_count_2)

    def _compute_vehicle_libre_count(self):
        obj = self.env['vehicle.libre']
        for serv in self:
            _logger.info("Helooooooooooooooooooooooooooooooooooo")
            _logger.info(serv[0])
            _logger.info(serv.id)
            _logger.info(obj.vehicle_id)
            obj_fleet = self.env['vehicle.libre'].search([('vehicle_id', '=', serv.id)])
            if obj_fleet:
                serv.vehicle_libre_count = obj.search_count([('vehicle_id', '=', serv.id)])
            else:
                serv.vehicle_libre_count = 0


class VehicleLibre(models.Model):
    _name = "vehicle.libre"
    _description = "Vehicle Libre"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    first_name = fields.Char('Name',translate=True)
    user_id = fields.Many2one('res.partner', string="User")

    name = fields.Char('Name', default='/',
        copy=False, index=True , readonly=True,translate=True)
    note = fields.Text('Notes',translate=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    nationality = fields.Char("Nationality",translate=True)
    region = fields.Char("Region",translate=True)
    note = fields.Text("note",translate=True)
    city = fields.Char("City",translate=True)
    subcity = fields.Char("Sub City",translate=True)
    woreda = fields.Char("Woreda",translate=True)
    house_number = fields.Char("House Number",translate=True)
    phone_number = fields.Char("Phone Number",translate=True)
    plate_number = fields.Char("Plate Number",translate=True)
    previous_plate_number = fields.Char("Previous Plate Number",translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    vehicle_type = fields.Many2one('vehicle.type', string='Vehicle Type')

    made_in = fields.Many2one('maid.by', string="Made In")
    vehicle_model = fields.Many2one('fleet.vehicle.model', string='Vehicle Model')

    creation_date = fields.Date('Creation Date')
    chassis_number = fields.Char('Chassis Number',translate=True)
    motor_number = fields.Char('Motor Number',translate=True)
    parts_type = fields.Char("Parts Type",translate=True)
    color = fields.Many2one('color.color', string='Color')
    fuel_type = fields.Selection([('gasoline', 'Gasoline'),
                                  ('diesel', 'Diesel'),
                                  ('petrol', 'Petrol'),
                                  ('electric', 'Electric'),
                                  ('hybrid', 'Hybrid')], string='Fuel Type')
    engine_horse_power = fields.Char("Engine Horse Power",translate=True)
    total_weight = fields.Integer("Total Weight",translate=True)
    items_weight = fields.Integer('Single Weight',translate=True)
    cc = fields.Char("CC",translate=True)
    cylinder_amount = fields.Integer("Number of Cylinders",translate=True)
    allowed_work_type = fields.Char("Allowed Services Type",translate=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('register', 'Register'),
        ('expired', 'Expired')
          ], default='draft', string="Status")
    duty = fields.Selection([
        ('free', 'Duty free'),
        ('non', 'Duty Paid')
    ], string='Duty')
    history = fields.One2many('libre.history', 'rev', string='History ')




    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('libray.renwal')
        vals.update({'name': seq})

        return super(VehicleLibre, self).create(vals)

    @api.model
    def default_get(self, fields):
        res = super(VehicleLibre, self).default_get(fields)
        vehical_obj = self.env['fleet.vehicle']
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({
                'vehicle_id': self._context['active_id'] or False,
                'vehicle_type': vehicle.vechical_type_id.id,
                'vehicle_model': vehicle.model_id.id,
                'chassis_number': vehicle.vin_sn,
                'motor_number': vehicle.engine_no,
                'color': vehicle.vehical_color_id.id,
                'fuel_type': vehicle.fuel_type,
                'plate_number': vehicle.license_plate,
                'previous_plate_number': vehicle.license_plate,
                'engine_horse_power': str(vehicle.horsepower),
                'slender_amount': str(vehicle.cylinders),
                'cc': vehicle.cc,
                'items_weight': vehicle.items_weight,
                'total_weight': vehicle.total_weight,

            })

        return res

    def update_info(self):
         self.vehicle_id.vechical_type_id = self.vehicle_type.id
         self.vehicle_id.model_id = self.vehicle_model.id
         self.vehicle_id.model_id = self.vehicle_model.id

    def set_draft(self):
        self.state = 'draft'

    def set_register(self):
        self.state = 'register'

    def set_expire(self):
        self.state = 'expired'
