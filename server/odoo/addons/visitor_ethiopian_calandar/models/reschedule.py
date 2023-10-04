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


class RescheduledTime(models.Model):
    _inherit = "rescheduled.time"


    ethiopian_from = fields.Date(string="Date", store=True) # date
    pagum_from = fields.Char(string="Date", store=True)
    is_pagum_from = fields.Boolean(default='True', string="Date")


    @api.model
    def create(self, vals):

        for i in range(0, len(pick1)):

            if i == (len(pick1) - 1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'], pick1[i]['month'], pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) == str:
                        vals['ethiopian_from'] = None
                        vals['date'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                        pick1.clear()
                    if type(Edate1) == date:
                        vals['date'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()


        try:
            if vals['date'] is not None:
                date1 = vals['date']
                date_time_obj1 = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj1[0]), int(date_time_obj1[1]),
                                                int(date_time_obj1[2]))

                if type(Edate1) == date:
                    vals['ethiopian_from'] = Edate1

                elif type(Edate1) == str:
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False

        except:
            pass      


        return super(RescheduledTime, self).create(vals)


    def write(self, vals):
        _logger.info("################# Write %s", vals)

        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                              int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
                vals['date'] = date_gr
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
            if vals['date'] is not None:
                date_str = vals['date']
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

        return super(RescheduledTime, self).write(vals)



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

