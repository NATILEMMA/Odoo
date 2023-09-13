import time
from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning


class PreventiveMaintenance(models.Model):
    _name = 'preventive.maintenance'
    _description = 'Preventive Maintenance'


    maintenance_name = fields.Char(string="maintenance name", translate=True)
    service_odometer = fields.Float(string='Minimum Odometer Value')
    service_odometer_2 = fields.Float(string='Maximum Odometer Value')
    vehicle_model = fields.Many2one('fleet.vehicle.model', string='model')
    date_start = fields.Date('Date From')
    service_type = fields.One2many("preventive.maintenance.line", "preventive", string='Service Type')
    time = fields.Float(string="Time")

    @api.onchange('time', 'service_type')
    def change_time_in_line(self):
       count = 0
       for line in self.service_type:
           count = count + 1
       for service in self.service_type:
           service.service_time = self.time/count

    @api.onchange('vehicle_model')
    def _compute_get_last_odoo(self):
       for rec in self:
        model = rec.vehicle_model.id

        last = self.env['preventive.maintenance'].search([('vehicle_model', '=', model)], limit=1, order="service_odometer_2 desc")
        rec.service_odometer = last.service_odometer_2


class PreventiveMaintenance(models.Model):
    _name = 'preventive.maintenance.line'
    _description = 'Preventive Maintenance.line'

    preventive = fields.Many2one("preventive.maintenance", string='preventive')
    vehicle_model = fields.Many2one('repair.type', string='Repair Type')
    service_time = fields.Float(string="Time", store=True)
    condition = fields.Selection(
       [('harsh', 'Harsh'),
        ('clean', 'clean')],
        required=True,
        store=True,
        string='Vehicle condition')
    type = fields.Selection([
        ('inspect', 'Inspect'),
        ('repair', 'Repair'),
        ('replace', 'Replace'),
        ('clean','Clean')],
        required=True,
        store=True,
        string='Maintenance operations')
    product_id = fields.Many2one('product.product', string='Part',
                                 domain="[('is_part', '=', True), ('type','!=', 'service')]")


