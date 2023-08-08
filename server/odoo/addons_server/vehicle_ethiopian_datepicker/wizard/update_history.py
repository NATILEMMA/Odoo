# See LICENSE file for full copyright and licensing details.
"""Update History Wizard."""

from datetime import datetime
import logging
from datetime import date
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
from ethiopian_date import EthiopianDateConverter
pick1 = []
pick2 = []
pick3 = []
pick4 = []



class UpdateEngineInfo(models.TransientModel):
    """Update Engine Info."""

    _inherit = 'update.engine.info'


# To use code for a single date in a wizard, 

# you should copy the code from line 39 to the end of the date_convert_and_set function, 



    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')


    
    @api.model
    def initial_date(self, data):
        date = datetime.now()
        data = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
        return data

    @api.model
    def date_convert_and_set(self,picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
       


    @api.constrains('changed_date')
    def check_engine_changed_date(self):
        """Method to check engine date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.vehicle_id.acquisition_date:
                if vehicle.changed_date < vehicle.vehicle_id.acquisition_date:
                    raise ValidationError('Engine Change Date Should Be '
                                          'Greater Than Vehicle Registration Date.')

    @api.model
    def default_get(self, fields):
        """Method Default Get."""
        vehical_obj = self.env['fleet.vehicle']
        res = super(UpdateEngineInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({'previous_engine_no': vehicle.engine_no or "",
                        'vehicle_id': self._context['active_id'] or False})
        return res

    def set_new_engine_info(self):
        """Method set new engine info."""
        _logger.info("***************pick1 %s",pick1)
        vehicle_obj = self.env['fleet.vehicle']

        engine_history_obj = self.env['engine.history']
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        ethiopian_from = Edate1
                        pick1.clear()
                    if type(Edate1) ==   date:
                        ethiopian_from = Edate1

                        pick1.clear()
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                _logger.info("********ethiopian_from*******%s",ethiopian_from)
                _logger.info("********changed_date*******%s",wiz_data.changed_date)

                vehicle.write({'engine_no': wiz_data.new_engine_no or ""})
                if wiz_data.ethiopian_from is not False:
                    engine_history_obj.create({
                        'previous_engine_no': wiz_data.previous_engine_no or "",
                        'new_engine_no': wiz_data.new_engine_no or "",
                        'note': wiz_data.note or '',
                        'changed_date': ethiopian_from,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
                else:
                     engine_history_obj.create({
                    'previous_engine_no': wiz_data.previous_engine_no or "",
                    'new_engine_no': wiz_data.new_engine_no or "",
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True


class UpdateColorInfo(models.TransientModel):
    """Update Color Info."""

    _name = 'update.color.info'
    _description = 'Update Color Info'

    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')
    previous_color_id = fields.Many2one('color.color', string="Previous Color")
    current_color_id = fields.Many2one('color.color', string="New Color")
    changed_date = fields.Date(string='Change Date',
                               default=datetime.now().date())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True,
                               string='Temp Bool for making previous \
                               color readonly')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.constrains('changed_date')
    def check_color_changed_date(self):
        """Method to check color changed date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.vehicle_id.acquisition_date:
                if vehicle.changed_date < vehicle.vehicle_id.acquisition_date:
                    raise ValidationError('Color Change Date Should Be '
                                          'Greater Than Vehicle Registration Date.')

    @api.model
    def default_get(self, fields):
        """Method default Get."""
        vehical_obj = self.env['fleet.vehicle']
        res = super(UpdateColorInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({'previous_color_id': vehicle.vehical_color_id and
                        vehicle.vehical_color_id.id or False,
                        'vehicle_id': self._context['active_id'] or False})
        return res

    def set_new_color_info(self):
        """Method set new color info."""
        vehicle_obj = self.env['fleet.vehicle']
        color_history_obj = self.env['color.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'vehical_color_id': wiz_data.current_color_id and
                    wiz_data.current_color_id.id or False
                })
                color_history_obj.create({
                    'previous_color_id': wiz_data.previous_color_id and
                    wiz_data.previous_color_id.id or False,
                    'current_color_id': wiz_data.current_color_id and
                    wiz_data.current_color_id.id or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True


class UpdateVinInfo(models.TransientModel):
    """Update Vin Info."""

    _name = 'update.vin.info'
    _description = 'Update Vin Info'

    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')
    previous_vin_no = fields.Char(string='Previous Vin No', size=124)
    new_vin_no = fields.Char(string="New Vin No", size=124)
    changed_date = fields.Date(default=datetime.now().date(),
                               string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True,
                               string='Temp Bool for making previous \
                                color readonly')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.model
    def default_get(self, fields):
        """Method default get."""
        vehical_obj = self.env['fleet.vehicle']
        res = super(UpdateVinInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({'previous_vin_no': vehicle.vin_sn or "",
                        'vehicle_id': self._context['active_id'] or False})
        return res

    def set_new_vin_info(self):
        """Method to set new vin info."""
        vehicle_obj = self.env['fleet.vehicle']
        vin_history_obj = self.env['vin.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({'vin_sn': wiz_data.new_vin_no or ""})
                vin_history_obj.create({
                    'previous_vin_no': wiz_data.previous_vin_no or "",
                    'new_vin_no': wiz_data.new_vin_no or "",
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True


class UpdateTireInfo(models.TransientModel):
    """Update Tire Info."""

    _name = 'update.tire.info'
    _description = 'Update Tire Info'

    previous_tire_size = fields.Char(string='Previous Tire Size', size=124)
    new_tire_size = fields.Char(string="New Tire Size", size=124)
    previous_tire_sn = fields.Char(string='Previous Tire S/N', size=124)
    new_tire_sn = fields.Char(string="New Tire S/N", size=124)
    previous_tire_issue_date = fields.Date(
        string='Previous Tire Issuance Date')
    new_tire_issue_date = fields.Date(string='New Tire Issuance Date')
    changed_date = fields.Date(string='Change Date',
                               default=datetime.now().date())
    note = fields.Text('Notes', translate=True)
    temp_bool = fields.Boolean(default=True, string='Temp Bool for making \
                                                previous Tire info readonly')
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.constrains('previous_tire_issue_date', 'new_tire_issue_date')
    def check_new_tire_issue_date(self):
        """Method to check new tire issue date."""
        for vehicle in self:
            if vehicle.previous_tire_issue_date and \
                    vehicle.new_tire_issue_date:
                if vehicle.new_tire_issue_date < \
                        vehicle.previous_tire_issue_date:
                    raise ValidationError('New Tire Issuance Date Should Be '
                                          'Greater Than Previous Tire Issuance Date.')

    @api.constrains('changed_date', 'new_tire_issue_date')
    def check_tire_changed_date(self):
        """Method to check tire changed date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.new_tire_issue_date:
                if vehicle.changed_date < vehicle.new_tire_issue_date:
                    raise ValidationError('Tire Change Date Should Be '
                                          'Greater Than New Tire Issuance Date.')

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        vehical_obj = self.env['fleet.vehicle']
        res = super(UpdateTireInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({
                'previous_tire_size': vehicle.tire_size or "",
                'previous_tire_sn': vehicle.tire_srno or "",
                "previous_tire_issue_date": vehicle.tire_issuance_date,
                'vehicle_id': self._context['active_id'] or False})
        return res

    def set_new_tire_info(self):
        """Method set new tire info."""
        vehicle_obj = self.env['fleet.vehicle']
        tire_history_obj = self.env['tire.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'tire_size': wiz_data.new_tire_size or "",
                    'tire_srno': wiz_data.new_tire_sn or "",
                    'tire_issuance_date': wiz_data.new_tire_issue_date})
                tire_history_obj.create({
                    'previous_tire_size': wiz_data.previous_tire_size or "",
                    'new_tire_size': wiz_data.new_tire_size or "",
                    'previous_tire_sn': wiz_data.previous_tire_sn or "",
                    'new_tire_sn': wiz_data.new_tire_sn or "",
                    'previous_tire_issue_date':
                    wiz_data.previous_tire_issue_date or False,
                    'new_tire_issue_date':
                    wiz_data.new_tire_issue_date or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True


class UpdateBatteryInfo(models.TransientModel):
    """Update Battery Info."""

    _name = 'update.battery.info'
    _description = 'Update Battery Info'

    previous_battery_size = fields.Char(string='Previous Battery Size',
                                        size=124)
    new_battery_size = fields.Char(string="New Battery Size", size=124)
    previous_battery_sn = fields.Char(string='Previous Battery S/N', size=124)
    new_battery_sn = fields.Char(string="New Battery S/N", size=124)
    previous_battery_issue_date = fields.Date(
        string='Previous Battery Issuance Date')
    new_battery_issue_date = fields.Date(string='New Battery Issuance Date')
    changed_date = fields.Date(string='Change Date',
                               default=datetime.now().date())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True,
                               string='Temp Bool for making previous \
                                             Battery info readonly')
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Work Order')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.constrains('previous_battery_issue_date', 'new_battery_issue_date')
    def check_new_battery_issue_date(self):
        """Method to check new battery issue date."""
        for vehicle in self:
            if vehicle.previous_battery_issue_date and \
                    vehicle.new_battery_issue_date:
                if vehicle.new_battery_issue_date < \
                        vehicle.previous_battery_issue_date:
                    raise ValidationError('New Battery Issuance Date Should Be '
                                          'Greater Than Previous Battery Issuance Date.')

    @api.constrains('changed_date', 'new_battery_issue_date')
    def check_battery_changed_date(self):
        """Method to check battery chanaged date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.new_battery_issue_date:
                if vehicle.changed_date < vehicle.new_battery_issue_date:
                    raise ValidationError('Battery Change Date Should Be '
                                          'Greater Than New Battery Issuance Date.')

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        vehical_obj = self.env['fleet.vehicle']
        res = super(UpdateBatteryInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({
                'previous_battery_size': vehicle.battery_size or "",
                'previous_battery_sn': vehicle.battery_srno or "",
                "previous_battery_issue_date": vehicle.battery_issuance_date,
                'vehicle_id': self._context['active_id'] or False})
        return res

    def set_new_battery_info(self):
        """Method to set new battery info."""
        vehicle_obj = self.env['fleet.vehicle']
        battery_history_obj = self.env['battery.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'battery_size': wiz_data.new_battery_size or "",
                    'battery_srno': wiz_data.new_battery_sn or "",
                    'battery_issuance_date': wiz_data.new_battery_issue_date})
                battery_history_obj.create({
                    'previous_battery_size':
                    wiz_data.previous_battery_size or "",
                    'new_battery_size': wiz_data.new_battery_size or "",
                    'previous_battery_sn': wiz_data.previous_battery_sn or "",
                    'new_battery_sn': wiz_data.new_battery_sn or "",
                    'previous_battery_issue_date':
                    wiz_data.previous_battery_issue_date or False,
                    'new_battery_issue_date':
                    wiz_data.new_battery_issue_date or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True
