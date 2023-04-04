
import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []


class Complaints(models.Model):
    _inherit="member.complaint"

    ethiopian_date_of_remedy = fields.Date(string="Ethiopian date of remedy")
    ethiopian_date_of_remedy_subcity = fields.Date(string="Ethiopian Date of Remedy for Subcity")
    ethiopian_date_of_remedy_city = fields.Date(string="Ethiopian Date of Remedy for City")

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    vals['date_of_remedy'] = date1
                    vals['ethiopian_date_of_remedy'] = Edate1
                    pick1.clear()

        for i in range(0, len(pick2)):
  
            if i == (len(pick2)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick2[i]['pick'] == 2:
                    vals['date_of_remedy_subcity'] = date1
                    vals['ethiopian_date_of_remedy_subcity'] = Edate1
                    pick2.clear()

        for i in range(0, len(pick3)):
  
            if i == (len(pick3)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick3[i]['year'],pick3[i]['month'],pick3[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick3[i]['pick'] == 3:
                    vals['date_of_remedy_city'] = date1
                    vals['ethiopian_date_of_remedy_city'] = Edate1
                    pick3.clear()

        res =  super(Complaints, self).create(vals)
        try:
            if res.date_of_remedy is not None:
                date1 = res.date_of_remedy
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                res.ethiopian_date_of_remedy = Edate1
        except:
            pass
       
        return res



    def write(self, vals):
        for record in self:
            try:
                if vals['date_of_remedy'] is not None:
                    date_str = vals['date_of_remedy']
                    if type(vals['date_of_remedy']) == str:
                        date_time_obj = date_str.split('-')
                        if vals['date_of_remedy'] >= record.create_date.date():
                            days = (vals['date_of_remedy'] - record.create_date.date()).days
                            record.duration_of_remedy = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))
                        Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                        vals['ethiopian_date_of_remedy'] = Edate
                    else:
                        if vals['date_of_remedy'] >= record.create_date.date():
                            days = (vals['date_of_remedy'] - record.create_date.date()).days
                            record.duration_of_remedy = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))                   

                        Edate = EthiopianDateConverter.to_ethiopian(date_str.year,date_str.month,date_str.day)
                        vals['ethiopian_date_of_remedy'] = Edate
            except:
                pass

            try:
                if vals['date_of_remedy_subcity'] is not None:
                    date_str = vals['date_of_remedy_subcity']
                    if type(vals['date_of_remedy_subcity']) == str:
                        date_time_obj = date_str.split('-')
                        if vals['date_of_remedy_subcity'] >= record.create_date.date():
                            days = (vals['date_of_remedy_subcity'] - record.create_date.date()).days
                            record.duration_of_remedy_subcity = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))
                        Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                        vals['ethiopian_date_of_remedy_subcity'] = Edate
                    else:
                        if vals['date_of_remedy_subcity'] >= record.create_date.date():
                            days = (vals['date_of_remedy_subcity'] - record.create_date.date()).days
                            record.duration_of_remedy_subcity = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))                   

                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    vals['ethiopian_date_of_remedy_subcity'] = Edate
            except:
                pass

            try:
                if vals['date_of_remedy_city'] is not None:
                    date_str = vals['date_of_remedy_city']
                    if type(vals['date_of_remedy_city']) == str:
                        date_time_obj = date_str.split('-')
                        if vals['date_of_remedy_city'] >= record.create_date.date():
                            days = (vals['date_of_remedy_city'] - record.create_date.date()).days
                            record.duration_of_remedy_city = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))
                        Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                        vals['ethiopian_date_of_remedy_city'] = Edate
                    else:
                        if vals['date_of_remedy_city'] >= record.create_date.date():
                            days = (vals['date_of_remedy_city'] - record.create_date.date()).days
                            record.duration_of_remedy_city = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))                   

                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    vals['ethiopian_date_of_remedy_city'] = Edate
            except:
                pass

        return super(Complaints, self).write(vals)


    @api.model
    def date_convert_and_set(self,picked_date):
        try:
            dd = picked_date['url'].split('id=')
            id = str(dd[1]).split('&')
            m = picked_date['url'].split('model=')
            mm = m[1].split('&')
            if len(id[0]) <= 0:
                _logger.info("################# not fund")

            else:
                models = mm[0]
                search = self.env[models].search([('id','=',id[0])])
                date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
                date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                if models == "member.complaint":
                    if picked_date['pick'] == 1:
                        search.update({
                            'date_of_remedy': date_gr,
                            'ethiopian_date_of_remedy': date
                            })
                        search.action_reload_page()
                            
                    if picked_date['pick'] == 2:
                        search.update({
                            'date_of_remedy_subcity': date_gr,
                            'ethiopian_date_of_remedy_subcity':date
                            })
                        search.action_reload_page()

                    if picked_date['pick'] == 3:
                        search.update({
                            'date_of_remedy_city': date_gr,
                            'ethiopian_date_of_remedy_city':date
                            })
                        search.action_reload_page()                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
        except:
            pass
            
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        _logger.info(str(date_gr) + " " + str(f"{time}"))
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
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)







