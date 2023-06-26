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


class Complaints(models.Model):
    _inherit="member.complaint"

    ethiopian_date_of_remedy = fields.Date(string="Date of remedy")
    pagum_date_of_remedy = fields.Char(string="Date of remedy")
    is_pagum_date_of_remedy = fields.Boolean(default='True', string="Date of remedy")

    ethiopian_date_of_remedy_subcity = fields.Date(string="Date of remedy for Subcity")
    pagum_date_of_remedy_subcity = fields.Char(string="Date of remedy for Subcity")
    is_pagum_date_of_remedy_subcity = fields.Boolean(default='True', string="Date of remedy for Subcity")

    ethiopian_date_of_remedy_city = fields.Date(string="Date of remedy for City")
    pagum_date_of_remedy_city = fields.Char(string="Date of remedy for City")
    is_pagum_date_of_remedy_city = fields.Boolean(default='True', string="Date of remedy for City")




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
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_date_of_remedy'] = None
                        vals['date_of_remedy'] = date1
                        vals['pagum_date_of_remedy'] = Edate1
                        vals['is_pagum_date_of_remedy'] = False
                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date_of_remedy'] = date1
                        vals['ethiopian_date_of_remedy'] = Edate1
                        pick1.clear()
       
        for i in range(0, len(pick2)):
            if i == (len(pick2)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick2[i]['pick'] == 2:
                    if type(Edate1) ==   str:
                        vals['ethiopian_date_of_remedy_subcity'] = None
                        vals['date_of_remedy_subcity'] = date1
                        vals['pagum_date_of_remedy_subcity'] = Edate1
                        vals['is_pagum_date_of_remedy_subcity'] = False
                        pick2.clear()
                    if type(Edate1) ==   date:
                        vals['date_of_remedy_subcity'] = date1
                        vals['ethiopian_date_of_remedy_subcity'] = Edate1
                        pick2.clear()

        for i in range(0, len(pick3)):
            if i == (len(pick3)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick3[i]['year'],pick3[i]['month'],pick3[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick3[i]['pick'] == 3:
                    if type(Edate1) ==   str:
                        vals['ethiopian_date_of_remedy_city'] = None
                        vals['date_of_remedy_city'] = date1
                        vals['pagum_date_of_remedy_city'] = Edate1
                        vals['is_pagum_date_of_remedy_city'] = False
                        pick3.clear()
                    if type(Edate1) ==   date:
                        vals['date_of_remedy_city'] = date1
                        vals['ethiopian_date_of_remedy_city'] = Edate1
                        pick3.clear()


        res = super(Complaints, self).create(vals)
        try:
            if res.date_of_remedy:
                date1 = res.date_of_remedy
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if type(Edate1) == date:               
                    res.ethiopian_date_of_remedy = Edate1
                if type(Edate1) == str:
                    res.pagum_date_of_remedy =  Edate1
                    res.is_pagum_date_of_remedy = False                
        except:
            pass

        return res


    def write(self, vals):
        for record in self:
            _logger.info("############# Write:%s",vals)
                
            try:
                if vals['date_of_remedy'] is not None:
                    date_str = vals['date_of_remedy']
                    date_time_obj = date_str.split('-')
                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    if type(Edate) ==  str:
                        vals['ethiopian_date_of_remedy'] = None
                        vals['is_pagum_date_of_remedy'] = False
                        vals['pagum_date_of_remedy'] = Edate
                    else:
                        if date_str >= record.create_date.date():
                            days = (date_str - record.create_date.date()).days
                            record.duration_of_remedy = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))
                        vals['ethiopian_date_of_remedy'] = Edate
                        vals['is_pagum_date_of_remedy'] = True
                        vals['pagum_date_of_remedy'] = ' '
            except:
                pass
        

            try:
                if vals['date_of_remedy_subcity'] is not None:
                    date_str = vals['date_of_remedy_subcity']
                    date_time_obj = date_str.split('-')
                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    if type(Edate) ==  str:
                        vals['ethiopian_date_of_remedy_subcity'] = None
                        vals['is_pagum_date_of_remedy_subcity'] = False
                        vals['pagum_date_of_remedy_subcity'] = Edate
                    else:
                        if date_str >= record.create_date.date():
                            days = (date_str - record.create_date.date()).days
                            record.duration_of_remedy_subcity = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))
                        vals['ethiopian_date_of_remedy_subcity'] = Edate
                        vals['is_pagum_date_of_remedy_subcity'] = True
                        vals['pagum_date_of_remedy_subcity'] = ' '
            except:
                pass


            try:
                if vals['date_of_remedy_city'] is not None:
                    date_str = vals['date_of_remedy_city']
                    date_time_obj = date_str.split('-')
                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    if type(Edate) ==  str:
                        vals['ethiopian_date_of_remedy_city'] = None
                        vals['is_pagum_date_of_remedy_city'] = False
                        vals['pagum_date_of_remedy_city'] = Edate
                    else:
                        if date_str >= record.create_date.date():
                            days = (date_str - record.create_date.date()).days
                            record.duration_of_remedy_city = int(days)
                        else:
                            raise ValidationError(_('Pick A Date After The Date It Was Created'))
                        vals['ethiopian_date_of_remedy_city'] = Edate
                        vals['is_pagum_date_of_remedy_city'] = True
                        vals['pagum_date_of_remedy_city'] = ' '
            except:
                pass


            # self.action_reload_page()
        return super(Complaints, self).write(vals)


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
                    if models == "member.complaint":
                        if picked_date['pick'] == 1:
                            if int(picked_date['month']) == 13:
                                search.update({
                                    'date_of_remedy': date_gr,
                                    'pagum_date_of_remedy': date,
                                    'is_pagum_date_of_remedy': False,
                                    'ethiopian_date_of_remedy': None
                                })
                                search.action_reload_page()
                            elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
                                search.update({
                                    'date_of_remedy': date_gr,
                                    'pagum_date_of_remedy': date,
                                    'is_pagum_date_of_remedy': False,
                                    'ethiopian_date_of_remedy': None
                                })
                                search.action_reload_page()
                            else:
                                search.update({
                                    'date_of_remedy': date_gr,
                                    'ethiopian_date_of_remedy': date,
                                    'is_pagum_date_of_remedy': True,
                                    'pagum_date_of_remedy': " "
                                })
                                search.action_reload_page()

                        if picked_date['pick'] == 2:
                            if int(picked_date['month']) == 13:
                                search.update({
                                    'date_of_remedy_subcity': date_gr,
                                    'pagum_date_of_remedy_subcity': date,
                                    'is_pagum_date_of_remedy_subcity': False,
                                    'ethiopian_date_of_remedy_subcity': None
                                })
                                search.action_reload_page()
                            elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
                                search.update({
                                    'date_of_remedy_subcity': date_gr,
                                    'pagum_date_of_remedy_subcity': date,
                                    'is_pagum_date_of_remedy_subcity': False,
                                    'ethiopian_date_of_remedy_subcity': None
                                })
                                search.action_reload_page()
                            else:
                                search.update({
                                    'date_of_remedy_subcity': date_gr,
                                    'ethiopian_date_of_remedy_subcity': date,
                                    'is_pagum_date_of_remedy_subcity': True,
                                    'pagum_date_of_remedy_subcity': " "
                                })
                                search.action_reload_page()

                        if picked_date['pick'] == 3:
                            if int(picked_date['month']) == 13:
                                search.update({
                                    'date_of_remedy_city': date_gr,
                                    'pagum_date_of_remedy_city': date,
                                    'is_pagum_date_of_remedy_city': False,
                                    'ethiopian_date_of_remedy_city': None
                                })
                                search.action_reload_page()
                            elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
                                search.update({
                                    'date_of_remedy_city': date_gr,
                                    'pagum_date_of_remedy_city': date,
                                    'is_pagum_date_of_remedy_city': False,
                                    'ethiopian_date_of_remedy_city': None
                                })
                                search.action_reload_page()
                            else:
                                search.update({
                                    'date_of_remedy_city': date_gr,
                                    'ethiopian_date_of_remedy_city': date,
                                    'is_pagum_date_of_remedy_city': True,
                                    'pagum_date_of_remedy_city': " "
                                })
                                search.action_reload_page()

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
            pick4.append(data)