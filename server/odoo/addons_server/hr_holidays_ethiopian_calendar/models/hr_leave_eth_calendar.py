import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
import psycopg2


_logger = logging.getLogger(__name__)

pick1 = []
pick2 = []
pick3 = []
pick4 = []



class HolidaysRequest(models.Model):
    _inherit = "hr.leave"


    ethiopian_from = fields.Date(string="Request Start Date", store=True) # request_date_from
    pagum_from = fields.Char(string="Request Start Date", store=True)
    is_pagum_from = fields.Boolean(default='True', string="Request Start Date")


    ethiopian_to = fields.Date(string="Request End Date", store=True) #  request_date_to
    pagum_to = fields.Char(string="Request End Date", store=True)
    is_pagum_to = fields.Boolean(default='True', string="Request End Date")


    @api.model
    def create(self, vals):
        print("psycopg version",psycopg2.__version__)
        for i in range(0, len(pick1)):
            

            if i == (len(pick1) - 1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'], pick1[i]['month'], pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) == str:
                        vals['ethiopian_from'] = None
                        vals['request_date_from'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                        pick1.clear()
                    if type(Edate1) == date:
                        vals['request_date_from'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()


        for i in range(0, len(pick2)):
           
            
            if i == (len(pick2) - 1):
                date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'], pick2[i]['month'], pick2[i]['day'])
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year, date2.month, date2.day)
                
       
                if pick2[i]['pick'] == 2:
                    if type(Edate2) == str:
                        vals['ethiopian_to'] = None
                        vals['request_date_to'] = date2
                        vals['pagum_to'] = Edate2
                        vals['is_pagum_to'] = False
                        pick2.clear()
                    if type(Edate2) == date:
                        vals['request_date_to'] = date2
                        vals['ethiopian_to'] = Edate2
                        pick2.clear()

        try:
            if vals['request_date_from'] is not None:
                date1 = vals['request_date_from']
                date_time_obj1 = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj1[0]), int(date_time_obj1[1]),
                                                int(date_time_obj1[2]))

                if type(Edate1) == date:
                    vals['ethiopian_from'] = Edate1

                elif type(Edate1) == str:
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False

            if vals['request_date_to'] is not None:
                date2 = vals['request_date_to']
                date_time_obj2 = date2.split('-')
                day = date_time_obj2[2].split(' ')
                Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                            int(day[0]))

                if type(Edate2) == date:
                    vals['ethiopian_to'] = Edate2
                elif type(Edate2) == str:
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_to'] = False

                else:
                    pass

        except:
            pass
        
        print(vals.get('ethiopian_from'),vals.get('ethiopian_to') )
        if vals.get('ethiopian_from') and vals.get('ethiopian_to') and vals.get('ethiopian_from') <= vals.get('ethiopian_to'):
           print(vals.get('ethiopian_to') - vals.get('ethiopian_from'))
           vals['number_of_days'] = float((vals.get('ethiopian_to') - vals.get('ethiopian_from')).days)
        elif not vals.get('is_pagum_from') and not vals.get('is_pagum_to') and vals.get('pagum_from') <= vals.get('pagum_to'):
            vals['number_of_days'] = float((datetime.strptime(vals.get('pagum_to'), "%Y-%m-%d") - datetime.strptime(vals.get('pagum_from'), "%Y-%m-%d")).days)
        elif not vals.get('is_pagum_from'):
            start_date = datetime.strptime(vals.get('pagum_from'), "%Y-%m-%d")
            
            if vals.get('ethiopian_to') >= start_date:
                    vals['number_of_days'] = float((vals.get('ethiopian_to') - start_date).days)
            else:
                raise exceptions.ValidationError(_("The start date and end date is not are misplaced causing negative error! 1"))
        elif not vals.get('is_pagum_to'):
            end_date = datetime.strptime(vals.get('pagum_to'), "%Y-%m-%d")
            
            if vals.get('ethiopian_from') <= end_date:
                vals['number_of_days'] = float((vals.get('ethiopian_from') - end_date).days)
            else:
                raise exceptions.ValidationError(_("The start date and end date is not are misplaced causing negative error! 2"))
        else:
            raise exceptions.ValidationError(_("The start date and end date is not are misplaced causing negative error! 3"))

        res = super(HolidaysRequest, self).create(vals)
        

        res._onchange_request_parameters()
        return res


    def write(self, vals):
        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                              int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
                vals['request_date_from'] = date_gr
                if type(Edate1) == str:
                    vals['ethiopian_from'] = None
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False
                if type(Edate1) == date:
                    vals['ethiopian_from'] = Edate1
                    vals['pagum_from'] = None
                    vals['is_pagum_from'] = True

        except:
            pass
        try:
            if vals['request_date_from'] is not None:
                date_str = vals['request_date_from']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                            int(date_time_obj[2]))

                if type(Edate) == str:
                    vals['ethiopian_from'] = None
                    vals['is_pagum_from'] = False
                    vals['pagum_from'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_from'] = Edate
                    vals['is_pagum_from'] = True
                    vals['pagum_from'] = ' '

        except:
            pass

        try:
            if vals['ethiopian_to'] is not None:
                date_str = vals['ethiopian_to']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                              int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
                vals['request_date_to'] = date_gr
                if type(Edate1) == str:
                    vals['ethiopian_to'] = None
                    vals['pagum_to'] = Edate1
                    vals['is_pagum_to'] = False
                if type(Edate1) == date:
                    vals['ethiopian_to'] = Edate1
                    vals['pagum_to'] = None
                    vals['is_pagum_to'] = True
        except:
            pass

        try:
            if vals['request_date_to'] is not None:

                date_str = vals['request_date_to']
                date_time_obj = date_str.split('-')
                day = date_time_obj[2].split(' ')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                            int(day[0]))

                if type(Edate) == str:
                    vals['ethiopian_to'] = None
                    vals['is_pagum_to'] = False
                    vals['pagum_to'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_to'] = Edate
                    vals['is_pagum_to'] = True
                    vals['pagum_to'] = ' '
        except:
            pass

        return super(HolidaysRequest, self).write(vals)
    
    
    @api.model
    def initial_date(self, data):
        
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@",self)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@",data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        print(id, "this is id", len(id[0]))
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            print("date return", date)
            data = {
                    'from': date,
                    'to': date,
                 }
            return data
        
        else:
            print("in the else")
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            From = []
            to = []
            three = []
            four = []
            print(search)

            # For initial date to widget One
            if search.ethiopian_from != False and search.pagum_from == False:
                From.append(search.ethiopian_from)
            if search.ethiopian_from == False and search.pagum_from != False:
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2]+'-'+date_from_str[0]+'-'+date_from_str[1]
                From.append(date_from)
            if search.ethiopian_from == False and search.pagum_from == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                From.append(today)

            # For initial date to widget Two
            if search.ethiopian_to != False and search.pagum_to == False:
                to.append(search.ethiopian_to)
            if search.ethiopian_to == False and search.pagum_to != False:
                date_to_str = str(search.pagum_to).split('/')
                date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
                to.append(date_to)
            if search.ethiopian_to == False and search.pagum_to == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                to.append(today)

            data = {
                'from': From[0],
                'to': to[0],
            }
        
            print("data ********")
            print(data)
            print("data **********")
           
            return data

    # @api.model
    # def initial_date(self, data):
    #     date = datetime.now()
    #     data = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
    #     return data
    
    @api.model
    def date_convert_and_set(self, picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date, time = str(datetime.now()).split(" ")
        dd, mm, yy = picked_date['day'], picked_date['month'], picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
        date = {"data": f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}", "date": date}
        data = {
            'day': picked_date['day'],
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
        if picked_date['pick'] == 4:
            pick3.append(data)