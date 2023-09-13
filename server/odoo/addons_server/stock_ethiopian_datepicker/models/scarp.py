import random
import string
import werkzeug.urls
from odoo import tools
from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []





class StockScrap(models.Model):
    _inherit = "stock.scrap"

    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')



    def write(self, vals):
        _logger.info("############# Write:%s",vals)
        try:
            if vals['state'] == 'done':
                date1 = datetime.now()
                date_time_obj = str(date1).split(' ')
                date_time_obj = date_time_obj[0].split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                vals['date_done'] = date1
                if type(Edate1) ==   str:
                    vals['ethiopian_from'] = None
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                    vals['ethiopian_from'] = Edate1
                    vals['pagum_from'] = None
                    vals['is_pagum_from'] = True
                
                pass
        except:
            pass
        return super(StockScrap, self).write(vals)
    
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
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            _logger.info("################# d: %s",date)

            return {'from': date, 'to': date}
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            if search.ethiopian_from != False and search.pagum_from == False:
                _logger.info("################# T")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': search.ethiopian_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from != False:
                _logger.info("#################  T pa")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2]+'-'+ date_from_str[0]+'-'+ date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': date_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from == False:
                _logger.info("#################  F")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': today}
            else:
                date = datetime.now()
                date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
                _logger.info("################# d: %s",date)

                return date

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
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)
        if picked_date['pick'] == 4:
            pick3.append(data)

