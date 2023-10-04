import random
import string
import werkzeug.urls
from odoo import tools
from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging
_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []
pick11 = []





class AccountMove(models.Model):
    _inherit = "account.move"

    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')

    ethiopian_to = fields.Date(string="in ethiopian date")
    pagum_to = fields.Char(string="in ethiopian date")
    is_pagum_to = fields.Boolean(default='True')


    ethiopian_three = fields.Date(string="in ethiopian date")
    pagum_three = fields.Char(string="in ethiopian date")
    is_pagum_three = fields.Boolean(default='True')


    @api.model
    def create(self, vals):
        _logger.info("create %s",vals)

        _logger.info("FFFFFFFFFFFFFFFFFFFFF %s,%s",pick11,pick2)
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['date'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()

                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', vals['date']), ('date_to', '>=', vals['date'])], limit=1)
                if not active_time_frame.id:
                    raise ValidationError(_(
                        'please set Time frame for the journal'))
                else:
                    vals['time_frame'] = active_time_frame.id
                    vals['fiscal_year'] = active_time_frame.fiscal_year.id
        for i in range(0, len(pick2)):
            if i == (len(pick2)-1):

                date1 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick2[i]['pick'] == 2:
                    if type(Edate1) ==   str:
                        vals['ethiopian_to'] = None
                        vals['invoice_date'] = date1
                        vals['pagum_to'] = Edate1
                        vals['is_pagum_to'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['invoice_date'] = date1
                        vals['ethiopian_to'] = Edate1
                        pick1.clear()

        for i in range(0, len(pick11)):
            if i == (len(pick11)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick11[i]['year'],pick11[i]['month'],pick11[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick11[i]['pick'] == 11:
                    if type(Edate1) ==   str:
                        vals['ethiopian_three'] = None
                        vals['invoice_date_due'] = date1
                        vals['pagum_three'] = Edate1
                        vals['is_pagum_three'] = False

                        pick11.clear()
                    if type(Edate1) ==   date:
                        vals['invoice_date_due'] = date1
                        vals['ethiopian_three'] = Edate1
                        pick11.clear()
               
        try:
            if vals['date'] is not None:
                date1 = vals['date']
                date_time_obj = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate1) ==   date:
                    vals['ethiopian_to'] = Edate1
                elif type(Edate1) ==   str :
                    vals['pagum_to'] = Edate1
                    vals['is_pagum_to'] = False

                else:
                    pass
                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', vals['date']), ('date_to', '>=', vals['date'])], limit=1)
                if not active_time_frame.id:
                    raise ValidationError(_(
                        'please set Time frame for the journal'))
                else:
                    vals['time_frame'] = active_time_frame.id
                    vals['fiscal_year'] = active_time_frame.fiscal_year.id
        except:
            pass
        try:
            if vals['invoice_date'] is not None:
                date1 = vals['invoice_date']
                date_time_obj = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate1) ==   date:
                    vals['ethiopian_to'] = Edate1
                elif type(Edate1) ==   str :
                    vals['pagum_to'] = Edate1
                    vals['is_pagum_to'] = False

                else:
                    pass
        except:
            pass
        try:
            if vals['invoice_date_due'] is not None:
                date1 = vals['invoice_date_due']
                _logger.info("$$$$$$$$$ %s",vals['invoice_date'] )
                date_time_obj = str(date1).split('-')
                # date_time_obj = date_time_obj[0].split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate1) ==   str:
                    vals['ethiopian_three'] = None
                    vals['pagum_three'] = Edate1
                    vals['is_pagum_three'] = False
                if type(Edate1) ==   date:
                    vals['ethiopian_three'] = Edate1
                    vals['pagum_three'] = None
                    vals['is_pagum_three'] = True
                
        except:
            pass
        return super(AccountMove, self).create(vals)
    


    def write(self, vals):
        _logger.info("wrrrrrrrrrrrrrr %s",vals)
                 
        try:
            if vals['date'] is not None:
                date_str = vals['date']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_from'] = Edate1
                        vals['pagum_from'] = None
                        vals['is_pagum_from'] = True

                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', vals['date']), ('date_to', '>=', vals['date'])], limit=1)
                if not active_time_frame.id:
                    pass
                else:
                    self['time_frame'] = active_time_frame
                    self['fiscal_year'] = active_time_frame.fiscal_year.id
        except:
            pass

        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_from'] = Edate1
                        vals['pagum_from'] = None
                        vals['is_pagum_from'] = True

           
                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', vals['date']), ('date_to', '>=', vals['date'])], limit=1)
                if not active_time_frame.id:
                    pass
                else:
                    self['time_frame'] = active_time_frame
                    self['fiscal_year'] = active_time_frame.fiscal_year.id
        except:
            pass

                
        
        try:
            if vals['invoice_date'] is not None:
                date_str = vals['invoice_date']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['invoice_date'] = date_gr
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
            if vals['ethiopian_to'] is not None:
                date_str = vals['ethiopian_to']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['invoice_date'] = date_gr
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
            if vals['invoice_date_due'] is not None:
                date_str = vals['invoice_date_due']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['invoice_date_due'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_three'] = None
                        vals['pagum_three'] = Edate1
                        vals['is_pagum_three'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_three'] = Edate1
                        vals['pagum_three'] = None
                        vals['is_pagum_three'] = True
        except:
            pass
        try:
            if vals['ethiopian_three'] is not None:
                date_str = vals['ethiopian_three']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['invoice_date_due'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_three'] = None
                        vals['pagum_three'] = Edate1
                        vals['is_pagum_three'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_three'] = Edate1
                        vals['pagum_three'] = None
                        vals['is_pagum_three'] = True
        except:
            pass
        return super(AccountMove, self).write(vals)
    


    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        date = datetime.now()
        wizdata = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
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

            if search.ethiopian_three != False and search.pagum_three == False:
                three.append(search.ethiopian_three)
            if search.ethiopian_three == False and search.pagum_three != False:
                date_to_str = str(search.pagum_three).split('/')
                date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
                three.append(date_to)
            if search.ethiopian_three == False and search.pagum_three == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                three.append(today)

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

              
            # # For initial date to widget widget

            if search.ethiopian_three != False and search.pagum_three == False:
                three.append(search.ethiopian_three)
            if search.ethiopian_three == False and search.pagum_three != False:
                date_to_str = str(search.pagum_three).split('/')
                date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
                three.append(date_to)
            if search.ethiopian_three == False and search.pagum_three == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                three.append(today)

            try:
                data = {
                    # 'data': wizdata,
                    'from': From[0],
                    'to': to[0],
                    'three': three[0],
                }

                # _logger.info("DDDDDDDDDDDDDDDDDDData %s",data)
            except:
                pass
            return data
    @api.model
    def date_convert_and_set(self,picked_date):
        _logger.info("############# Wrpicked_datepicked_datepicked_dateite:%s",picked_date)
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
                    Edate11 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                    _logger.info("################# yyyyyyyyyyyyyy %s fund",Edate11)
                    _logger.info("################# yyyyyyyyyyyyyy %s fund",type(Edate11))
                    types = type(Edate11)
                    _logger.info("################# yyyyyyyyyyyyyy %s fund",len(str(types)))


                    _logger.info("################# search %s fund",search.ethiopian_three)

                    if models == "account.move":
                        if picked_date['pick'] == 11:
                            # if type(Edate11) ==  str":
                            #     search.update({
                            #     'invoice_date_due': date_gr,
                            #     'ethiopian_three': Edate11,
                            #     'pagum_three': None,
                            #     'is_pagum_three': False
                            #     })
                            #     _logger.info("######### str ######## search %s fund",search.ethiopian_three)
                            # if type(Edate11) == date:
                            #     search.update({
                            #     'invoice_date_due': date_gr,
                            #     'ethiopian_three': Edate11,
                            #     'pagum_three': None,
                            #     'is_pagum_three': True
                            #     })
                                # search.action_reload_page()
                            if len(str(types)) ==  13:
                                search.update({
                                'invoice_date_due': date_gr,
                                'ethiopian_three': None,
                                'pagum_three': Edate11,
                                'is_pagum_three': False
                                })
                                _logger.info("######### str ######## search %s fund",search.pagum_three)
                            if len(str(types)) == 23:
                                search.update({
                                'invoice_date_due': date_gr,
                                'ethiopian_three': Edate11,
                                'pagum_three': None,
                                'is_pagum_three': True
                                })
                       
                                _logger.info("########## date ####### search %s fund",search.ethiopian_three)


                    

                    
                            
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
       

        except:
            pass

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
        if picked_date['pick'] == 11:
            pick11.append(data)

