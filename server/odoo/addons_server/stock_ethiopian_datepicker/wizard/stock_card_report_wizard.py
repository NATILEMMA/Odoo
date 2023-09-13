# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
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

class StockCardReportWizard(models.TransientModel):
    _inherit = "stock.card.report.wizard"

   
    ethiopian_to = fields.Date(string="in ethiopian date")
    pagum_to = fields.Char(string="in ethiopian date")
    is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")


    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')

    

    # ethiopian_three = fields.Date(string="in ethiopian date")
    # pagum_three = fields.Char(string="in ethiopian date")
    # is_pagum_three = fields.Boolean(default='True',string="in ethiopian date")
   
    
    
    # ethiopian_four = fields.Date(string="in ethiopian date")
    # pagum_four = fields.Char(string="in ethiopian date")
    # is_pagum_four = fields.Boolean(default='True')

   

    @api.model
    def create(self, vals):
        _logger.info("vals:%s",vals)
        _logger.info("pick1:%s",pick1)
        _logger.info("pick2:%s",pick2)

        

        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['date_start'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date_start'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()
                
        for i in range(0, len(pick2)):
        
            if i == (len(pick2)-1):
                date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate2))

                if pick2[i]['pick'] == 2:
                    if type(Edate2) ==   str:
                        vals['ethiopian_to'] = None
                        vals['date_deadline'] = date2
                        vals['pagum_to'] = Edate2
                        vals['is_pagum_to'] = False

                        pick2.clear()
                    if type(Edate2) ==   date:
                        vals['date_deadline'] = date2
                        vals['ethiopian_to'] = Edate2
                        pick2.clear()
        try:
            
            if vals['date_start'] is not None and vals['date_deadline'] is not None:
                date1 = vals['date_start']
                date2 = vals['date_deadline']
                date_time_obj = date1.split('-')
                date_time_obj2 = date2.split('-')

                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                _logger.info("^^^^^^^^^^^ %s",type(Edate2))
                if type(Edate1) ==   date and type(Edate2) ==   date:
                    vals['ethiopian_from'] = Edate1
                    vals['ethiopian_to'] = Edate2
                elif type(Edate1) == date and type(Edate2) == str:
                    vals['ethiopian_from'] = Edate1
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_to'] = False

                elif type(Edate1) ==   str and type(Edate2) ==   date:
                    vals['pagum_from'] = Edate1
                    vals['ethiopian_to'] = Edate2
                    vals['is_pagum_from'] = False

                elif type(Edate1) ==   str and type(Edate2) ==   str:
                    vals['pagum_from'] = Edate1
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_from'] = False
                    vals['is_pagum_to'] = False

                else:
                    pass
        except:
            pass
        return super(StockCardReportWizard, self).create(vals)

    def write(self, vals):
        _logger.info("############# Write:%s",vals)
        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date_start'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_from'] = Edate1
                        vals['pagum_from'] = None
                        vals['is_pagum_from'] = True
        except:
            pass
        try:

            if vals['ethiopian_to'] is not None:
                date_str = vals['ethiopian_to']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date_deadline'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_to'] = None
                        vals['pagum_to'] = Edate1
                        vals['is_pagum_to'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_to'] = Edate1
                        vals['pagum_to'] = None
                        vals['is_pagum_to'] = True
        except:
            pass
        try:
                       
            if vals['date_start'] is not None:
                date_str = vals['date_start']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                _logger.info("######     ############# %s",Edate)
                _logger.info("######     ############# %s",type(Edate))


                if type(Edate) ==   str:
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
            if vals['date_deadline'] is not None:
                
                date_str = vals['date_deadline']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate) ==   str:
                    vals['ethiopian_to'] = None
                    vals['is_pagum_to'] = False
                    vals['pagum_to'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_to'] = Edate
                    vals['is_pagum_to'] = True
                    vals['pagum_to'] = ' '
        except:
            pass
        return super(StockCardReportWizard, self).write(vals)


    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            return {'from': date, 'to': date}
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            From = []
            to = []
            three = []
            four = []

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

            # # For initial date to widget Three

            # if search.ethiopian_three != False and search.pagum_three == False:
            #     three.append(search.ethiopian_three)
            # if search.ethiopian_three == False and search.pagum_three != False:
            #     date_to_str = str(search.pagum_three).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     three.append(date_to)
            # if search.ethiopian_three == False and search.pagum_three == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     three.append(today)

            # # For initial date to widget Four

            # if search.ethiopian_four != False and search.pagum_four == False:
            #     four.append(search.ethiopian_four)
            # if search.ethiopian_four == False and search.pagum_four != False:
            #     date_to_str = str(search.pagum_four).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     four.append(date_to)
            # if search.ethiopian_four == False and search.pagum_four == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     four.append(today)

            try:
                data = {
                    'from': From[0],
                    'to': to[0],
                    # 'three': three[0],
                }

                _logger.info("DDDDDDDDDDDDDDDDDDData %s",data)
            except:
                pass
            return data
    

    @api.model
    def date_convert_and_set(self,picked_date):
        _logger.info("################# picked_date DATA %s", picked_date)

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


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    ethiopian_to = fields.Date(string="in ethiopian date")
    pagum_to = fields.Char(string="in ethiopian date")
    is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")


    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')

    


    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            return {'from': date, 'to': date}
        else:
            
            models = mm[0]
            search = self.env['wizadsa.'].search([('id','=',id[0])])
            From = []
            to = []
            three = []
            four = []

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

            # # For initial date to widget Three

            # if search.ethiopian_three != False and search.pagum_three == False:
            #     three.append(search.ethiopian_three)
            # if search.ethiopian_three == False and search.pagum_three != False:
            #     date_to_str = str(search.pagum_three).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     three.append(date_to)
            # if search.ethiopian_three == False and search.pagum_three == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     three.append(today)

            # # For initial date to widget Four

            # if search.ethiopian_four != False and search.pagum_four == False:
            #     four.append(search.ethiopian_four)
            # if search.ethiopian_four == False and search.pagum_four != False:
            #     date_to_str = str(search.pagum_four).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     four.append(date_to)
            # if search.ethiopian_four == False and search.pagum_four == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     four.append(today)

            try:
                data = {
                    'from': From[0],
                    'to': to[0],
                    # 'three': three[0],
                }

                _logger.info("DDDDDDDDDDDDDDDDDDData %s",data)
            except:
                pass
            return data
    