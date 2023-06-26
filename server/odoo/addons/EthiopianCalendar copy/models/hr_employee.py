
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
        
    
class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    """ 
    """

    ethiopian_to = fields.Date(string="in ethiopian date")
    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    pagum_to = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')
    is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")
 
    
    @api.model
    def create(self, vals):

        """
            Use this for loop to get your most recently selected date from the global append Ethiopian date.

            if your widget type are

            - ethiopian_calander_widget user pick1
            - ethiopian_calander_widget_two user pick2
            - ethiopian_calander_widget_three user pick3
            - ethiopian_calander_widget_four user pick4
           
       Pick1 is used in the for loop below because my view displays an Ethiopian date picker using the *ethiopian_calander_widget* widget type.

        """
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['birthday'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['birthday'] = date1
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
                        vals['visa_expire'] = date2
                        vals['pagum_to'] = Edate2
                        vals['is_pagum_to'] = False

                        pick2.clear()
                    if type(Edate2) ==   date:
                        vals['visa_expire'] = date2
                        vals['ethiopian_to'] = Edate2
                        pick2.clear()
        try:
            if vals['birthday'] is not None and vals['visa_expire'] is not None:
                date1 = vals['birthday']
                date2 = vals['visa_expire']
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
       
        return super(HrEmployeePrivate, self).create(vals)


    
    def write(self, vals):
        _logger.info("########dd##### Write:%s",vals)
        
        """
            This try-catch method is used to convert the Gregorian calendar to the Ethiopian calendar.
        
        """
        try:
            if vals['birthday'] is not None:
                date_str = vals['birthday']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
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
            if vals['visa_expire'] is not None:
                date_str = vals['visa_expire']
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
       
       
        # self.action_reload_page()
        return super(HrEmployeePrivate, self).write(vals)


    def action_reload_page(self):
        _logger.info("^^called^^")
     
        return {
                # 'type': 'ir.actions.act_url',
                # 'url': '/my/reload/',
                # 'target': 'new',
                # 'res_id': self.id,
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    """
        This date convert and set function converts and sets dates.

        takes the date value and  the widget type from javascript

        then append on global variables pick1, pick2, pick3, and pick 4 as the picked  widget type



        When in edit mode, the method will automatically set the selected Ethiopian date, convert it to Gregorian, and save it.
        
    """
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

            return date
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            _logger.info("################# From Date %s", search.ethiopian_from)
            _logger.info("################# From Date %s", search.ethiopian_to)

            if search.ethiopian_from is not None and search.ethiopian_to is not None:
                _logger.info("################# Both T")

                return {'from': search.ethiopian_from, 'to': search.ethiopian_to}
            elif search.ethiopian_from is None and search.ethiopian_to is not None:
                _logger.info("################# From - f  To - true")

                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': search.ethiopian_to}
            elif search.ethiopian_from is  None and search.ethiopian_to is not None:
                _logger.info("################# From - true  To - false")
                            
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': search.ethiopian_to}
            elif search.ethiopian_from is  None and search.ethiopian_to is  None:
                _logger.info("################# both- false")
                            
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
        try:
            dd = picked_date['url'].split('id=')
            id = str(dd[1]).split('&')
            m = picked_date['url'].split('model=')
            mm = m[1].split('&')
            if len(id[0]) <= 0:
                _logger.info("not fund")

            else:
                    _logger.info("lol")
                    models = mm[0]
                    search = self.env[models].search([('id','=',id[0])])
                    date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
                    date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                    if models == "hr.employee":
                        if picked_date['pick'] == 1:
                            if int(picked_date['month']) == 13:
                                search.update({
                                'birthday': date_gr,
                                'pagum_from': date,
                                'is_pagum_from': False,
                                'ethiopian_from': None
                                })
                                search.action_reload_page()
                            elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
                                search.update({
                                'birthday': date_gr,
                                'pagum_from': date,
                                'is_pagum_from': False,
                                'ethiopian_from': None

                                })
                                search.action_reload_page()
                            else:
                                search.update({
                                'birthday': date_gr,
                                'ethiopian_from': date,
                                'is_pagum_from': True,
                                'pagum_from': " "

                                })
                                search.action_reload_page()
                            
                            # return {
                            #         'type': 'ir.actions.client',
                            #         'tag': 'reload',
                            #     }
                            # self.env.cr.commit()
                            # return search
                            search.action_reload_page()
                            

                        if picked_date['pick'] == 2:
                            if int(picked_date['month']) == 13:

                                search.write({
                                    'visa_expire': date_gr,
                                    'pagum_to':date, 
                                    'is_pagum_to': False,
                                    'ethiopian_to': None
                                    })
                            elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
                                search.write({
                                'visa_expire': date_gr,
                                'pagum_to': date,
                                'is_pagum_to': False,
                                'ethiopian_to': None

                                })
                                search.action_reload_page()
                            else:
                                search.write({
                                    'visa_expire': date_gr,
                                    'ethiopian_to':date,
                                    'is_pagum_to': True,
                                    'pagum_to': " "


                                    })
                            # return {
                            #         'type': 'ir.actions.client',
                            #         'tag': 'reload',
                            #     }
                            # self.env.cr.commit()
                            # return search 
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
        if picked_date['pick'] == 4:
            pick3.append(data)



