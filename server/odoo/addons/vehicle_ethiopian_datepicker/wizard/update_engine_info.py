# See LICENSE file for full copyright and licensing details.
"""Update History Wizard."""

import logging
from datetime import datetime,date
from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError
_logger = logging.getLogger(__name__)
from ethiopian_date import EthiopianDateConverter


pick1 = []
pick2 = []
pick3 = []
pick4 = []


class EngineHistory(models.Model):
    """Model Engine History."""

    _inherit = 'engine.history'
    _description = 'Engine History for Vehicle'
    
    ethiopian_five = fields.Date(string="in ethiopian date")
    pagum_five = fields.Char(string="in ethiopian date")
    is_pagum_five = fields.Boolean(default='True')

    
    


class ColorHistory(models.Model):
    """Model Engine History."""

    _inherit = 'color.history'
    _description = 'Engine History for Vehicle'
    
    ethiopian_six = fields.Date(string="in ethiopian date")
    pagum_six = fields.Char(string="in ethiopian date")
    is_pagum_six = fields.Boolean(default='True')



class TireHistory(models.Model):
    """Model Engine History."""

    _inherit = 'tire.history'
    _description = 'Engine History for Vehicle'
    
    ethiopian_three = fields.Date(string="in ethiopian date")
    pagum_three = fields.Char(string="in ethiopian date")
    is_pagum_three = fields.Boolean(default='True')




class BatteryHistory(models.Model):
    """Model Engine History."""

    _inherit = 'battery.history'
    _description = 'Engine History for Vehicle'
    
    ethiopian_four = fields.Date(string="in ethiopian date")
    pagum_four = fields.Char(string="in ethiopian date")
    is_pagum_four = fields.Boolean(default='True')


    


class UpdateEngineInfo(models.TransientModel):
    """Update Engine Info."""

    _inherit = 'update.engine.info'



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

        vehicle_obj = self.env['fleet.vehicle']

        engine_history_obj = self.env['engine.history']
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                
               
                if pick1[i]['pick'] == 1:
                    for wiz_data in self:
                        if type(Edate1) ==   str:
                            wiz_data.pagum_from = Edate1
                            pick1.clear()
                        if type(Edate1) ==   date:
                            wiz_data.ethiopian_from = Edate1
               
                    
                pick1.clear()
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:

                vehicle.write({'engine_no': wiz_data.new_engine_no or ""})
                if wiz_data.pagum_from == False:
                    engine_history_obj.create({
                        'previous_engine_no': wiz_data.previous_engine_no or "",
                        'new_engine_no': wiz_data.new_engine_no or "",
                        'note': wiz_data.note or '',
                        'changed_date': wiz_data.changed_date,
                        'ethiopian_five': wiz_data.ethiopian_from,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
                else:
                    engine_history_obj.create({
                        'previous_engine_no': wiz_data.previous_engine_no or "",
                        'new_engine_no': wiz_data.new_engine_no or "",
                        'note': wiz_data.note or '',
                        'changed_date': wiz_data.changed_date,
                        'pagum_five': wiz_data.pagum_from,
                        'is_pagum_five': False,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
               
        return True



class UpdateColorInfo(models.TransientModel):
    """Update Color Info."""

    _inherit = 'update.color.info'
    _description = 'Update Color Info'
    
    
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


    def set_new_color_info(self):
        
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    for wiz_data in self:
                        if type(Edate1) ==   str:
                            wiz_data.pagum_from = Edate1
                            pick1.clear()
                        if type(Edate1) ==   date:
                            wiz_data.ethiopian_from = Edate1
                            pick1.clear()
                        
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
                if wiz_data.pagum_from == False:
                    color_history_obj.create({
                        'previous_color_id': wiz_data.previous_color_id and
                        wiz_data.previous_color_id.id or False,
                        'current_color_id': wiz_data.current_color_id and
                        wiz_data.current_color_id.id or False,
                        'note': wiz_data.note or '',
                        'changed_date': wiz_data.changed_date,
                        'ethiopian_six': wiz_data.ethiopian_from,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
                else: 
                    color_history_obj.create({
                    'previous_color_id': wiz_data.previous_color_id and
                    wiz_data.previous_color_id.id or False,
                    'current_color_id': wiz_data.current_color_id and
                    wiz_data.current_color_id.id or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'pagum_six': wiz_data.pagum_from,
                    'is_pagum_six': False,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True



class UpdateTireInfo(models.TransientModel):
    """Update Tire Info."""

    _inherit  = 'update.tire.info'
    _description = 'Update Tire Info'
    
    
    
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
    def set_new_tire_info(self):
        
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    for wiz_data in self:
                        if type(Edate1) ==   str:
                            wiz_data.pagum_from = Edate1
                            pick1.clear()
                        if type(Edate1) ==   date:
                            wiz_data.ethiopian_from = Edate1

                            pick1.clear()
        """Method set new tire info."""
        vehicle_obj = self.env['fleet.vehicle']
        tire_history_obj = self.env['tire.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                if wiz_data.pagum_from == False:
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
                        'ethiopian_three': wiz_data.ethiopian_from,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
                else:
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
                        'pagum_three': wiz_data.pagum_from,
                        'is_pagum_three': False,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
        return True


class UpdateBatteryInfo(models.TransientModel):
    """Update Battery Info."""

    _inherit  = 'update.battery.info'
    _description = 'Update Battery Info'
    
    
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


    
        
        

    def set_new_battery_info(self):
         
        
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    for wiz_data in self:
                        if type(Edate1) ==   str:
                            wiz_data.pagum_from = Edate1
                            pick1.clear()
                        if type(Edate1) ==   date:
                            wiz_data.ethiopian_from = Edate1

                            pick1.clear()
        """Method to set new battery info."""
        vehicle_obj = self.env['fleet.vehicle']
        battery_history_obj = self.env['battery.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                if wiz_data.pagum_from == False:
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
                        'ethiopian_four': wiz_data.ethiopian_from,
                        'workorder_id': wiz_data.workorder_id and
                        wiz_data.workorder_id.id or False,
                        'vehicle_id': vehicle.id})
                else:
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
                    'pagume_four': wiz_data.pagum_from,
                    'is_pagume_four': False,
                    'workorder_id': wiz_data.workorder_id and
                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id})
        return True


