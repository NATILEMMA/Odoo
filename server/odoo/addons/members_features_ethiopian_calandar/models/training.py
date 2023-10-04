import random
import string
import werkzeug.urls
from odoo import tools
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
all_values = {}



class MemberTraining(models.Model):
    _inherit = 'member.training'

    ethiopian_from = fields.Date(string="Start Date", store=True)
    pagum_from = fields.Char(string="Start Date", store=True)
    is_pagum_from = fields.Boolean(default='True', string="Start Date")

    ethiopian_to = fields.Date(string="End Date")
    pagum_to = fields.Char(string="End Date")
    is_pagum_to = fields.Boolean(default='True', string="End Date")


    @api.model
    def create(self, vals):

        for i in range(0, len(pick1)):

            if i == (len(pick1) - 1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'], pick1[i]['month'], pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) == str:
                        vals['ethiopian_from'] = None
                        vals['start_date'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                        pick1.clear()
                    if type(Edate1) == date:
                        vals['start_date'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()

        for i in range(0, len(pick2)):

            if i == (len(pick2) - 1):
                date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'], pick2[i]['month'], pick2[i]['day'])
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year, date2.month, date2.day)

                if pick2[i]['pick'] == 2:
                    if type(Edate2) == str:
                        vals['ethiopian_to'] = None
                        vals['end_date'] = date2
                        vals['pagum_to'] = Edate2
                        vals['is_pagum_to'] = False
                        pick2.clear()
                    if type(Edate2) == date:
                        vals['end_date'] = date2
                        vals['ethiopian_to'] = Edate2
                        pick2.clear()
                        
        try:
            if vals['start_date'] is not None:
                date1 = vals['start_date']
                date_time_obj = date1.split('-')

                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                             int(date_time_obj[2]))

                if type(Edate1) == date:
                    vals['ethiopian_from'] = Edate1

                elif type(Edate1) == str:
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False
                else:
                    pass

            if vals['end_date'] is not None:
                date2 = vals['end_date']
                date_time_obj2 = date2.split('-')

                Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]), int(date_time_obj2[1]),
                                                             int(date_time_obj2[2]))
                if type(Edate2) == date:  
                    vals['ethiopian_to'] = Edate2  
                elif type(Edate2) == str:
                    vals['ethiopian_to'] = Edate2
                    vals['is_pagum_from'] = False
                else:
                    pass
        except:
            pass

        return super(MemberTraining, self).create(vals)


    def write(self, vals):
        _logger.info("################# Write %s", vals)

        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                              int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
                vals['start_date'] = date_gr
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

            if vals['start_date'] is not None:
                date_str = vals['start_date']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                            int(date_time_obj[2]))
                _logger.info("######     ############# %s", Edate)
                _logger.info("######     ############# %s", type(Edate))

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
                vals['end_date'] = date_gr
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
            if vals['end_date'] is not None:

                date_str = vals['end_date']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                            int(date_time_obj[2]))
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
        return super(MemberTraining, self).write(vals)



    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            _logger.info("################# not fund")
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year, date.month, date.day)
            _logger.info("################# d: %s", date)

            return date
        else:

            models = mm[0]
            search = self.env[models].search([('id', '=', id[0])])
            if search.ethiopian_from != False and search.pagum_from == False and search.ethiopian_to != False and search.pagum_to == False:
                _logger.info("################# Both T")
                return {'from': search.ethiopian_from, 'to': search.ethiopian_to}
            elif search.ethiopian_from == False and search.pagum_from != False and search.ethiopian_to == False and search.pagum_to != False:
                _logger.info("################# Both T")
                date_from_str = str(search.pagum_from).split('/')
                date_to_str = str(search.pagum_to).split('/')
                date_from = date_from_str[2] + '-' + date_from_str[0] + '-' + date_from_str[1]
                date_to = date_to_str[2] + '-' + date_to_str[0] + '-' + date_to_str[1]
                return {'from': date_from, 'to': date_to}
            elif search.ethiopian_from == False and search.pagum_from == False and search.ethiopian_to != False and search.pagum_to == False:
                _logger.info("################# From - f  To - true")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': today, 'to': search.ethiopian_to}
            elif search.ethiopian_from == False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to != False:
                _logger.info("################# From - f  To - true")
                date_to_str = str(search.pagum_to).split('/')
                date_to = date_to_str[2] + '-' + date_to_str[0] + '-' + date_to_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': today, 'to': date_to}
            elif search.ethiopian_from != False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to != False:
                _logger.info("################# From - f  To - true p")
                date_to_str = str(search.pagum_to).split('/')
                date_to = date_to_str[2] + '-' + date_to_str[0] + '-' + date_to_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': search.ethiopian_from, 'to': date_to}
            elif search.ethiopian_from != False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to == False:
                _logger.info("################# From - true  To - false")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': search.ethiopian_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from != False and search.ethiopian_to == False and search.pagum_to == False:
                _logger.info("################# From - true  To - false")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2] + '-' + date_from_str[0] + '-' + date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': date_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from != False and search.ethiopian_to != False and search.pagum_to == False:
                _logger.info("################# From - true  To - false pa")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2] + '-' + date_from_str[0] + '-' + date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': date_from, 'to': search.ethiopian_to}
            elif search.ethiopian_from == False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to == False:
                _logger.info("################# both- false")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': today, 'to': today}

            else:
                date = datetime.now()
                date = EthiopianDateConverter.to_ethiopian(date.year, date.month, date.day)
                _logger.info("################# d: %s", date)


                return date

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