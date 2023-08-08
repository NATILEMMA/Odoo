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


class VehicleLibreInherited(models.Model):
    _inherit = 'vehicle.libre'

    ethiopian_three = fields.Date(string="in ethiopian date")
    pagum_three = fields.Char(string="in ethiopian date")
    is_pagum_three = fields.Boolean(default='True',string="in ethiopian date")
 

    @api.model
    def create(self, vals):
       
                
       
        for i in range(0, len(pick3)):
        
            if i == (len(pick3)-1):
                date3 = EthiopianDateConverter.to_gregorian(pick3[i]['year'],pick3[i]['month'],pick3[i]['day'])
                Edate3 = EthiopianDateConverter.to_ethiopian(date3.year,date3.month,date3.day)


                if pick3[i]['pick'] == 3:
                    if type(Edate3) == str:
                        vals['ethiopian_three'] = None
                        vals['creation_date'] = date3
                        vals['pagum_three'] = Edate3
                        vals['is_pagum_three'] = False

                       
                    if type(Edate3) == date:
                        
                        vals['creation_date'] = date3
                        vals['ethiopian_three'] = Edate3
                
                pick3.clear()
        


        try:
            
            if vals['ethiopian_three'] is not None:
                date1 = vals['ethiopian_three']
                date_time_obj = date1.split('-')
              
                date_gr_from = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr_from.year,date_gr_from.month,date_gr_from.day)

                vals['creation_date'] = date_gr_from
              
                if type(Edate1) == date :
                    vals['ethiopian_three'] = Edate1
                    vals['is_pagum_three'] = False
                    pick3.clear()
                elif type(Edate1) ==   str :
                    vals['pagum_three'] = Edate1    
                    vals['is_pagum_three'] = False
                    pick3.clear()
                else:
                    pass

        except:
            pass

    
        try:
            if vals['creation_date'] is not None :
                date1 = vals['creation_date']
                
                date_time_obj = date1.split('-')

                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                
                if type(Edate1) ==   date :
                    vals['ethiopian_three'] = Edate1
                 
                elif type(Edate1) ==   str :
                    vals['pagum_three'] = Edate1
                    vals['is_pagum_three'] = False

                else:
                    pass
        except:
            pass

        return super(VehicleLibreInherited, self).create(vals)

    def write(self, vals):
    


        try:
            if vals['ethiopian_three'] is not None:
                date_str = vals['ethiopian_three']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['creation_date'] = date_gr
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
            if vals['creation_date'] is not None:
                
                date_str = vals['creation_date']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate) == str:
                    vals['ethiopian_three'] = None
                    vals['is_pagum_three'] = False
                    vals['pagum_three'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_three'] = Edate
                    vals['is_pagum_three'] = True
                    vals['pagum_three'] = ' '
        except:
            pass

        return super(VehicleLibreInherited, self).write(vals)


    @api.model
    def initial_date(self, data):
        

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            return date
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            From = []
            to = []
            three = []
            four = []

            # # For initial date to widget One
            # if search.ethiopian_from != False and search.pagum_from == False:
            #     From.append(search.ethiopian_from)
            # if search.ethiopian_from == False and search.pagum_from != False:
            #     date_from_str = str(search.pagum_from).split('/')
            #     date_from = date_from_str[2]+'-'+date_from_str[0]+'-'+date_from_str[1]
            #     From.append(date_from)
            # if search.ethiopian_from == False and search.pagum_from == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     From.append(today)

            # # For initial date to widget Two
            # if search.ethiopian_to != False and search.pagum_to == False:
            #     to.append(search.ethiopian_to)
            # if search.ethiopian_to == False and search.pagum_to != False:
            #     date_to_str = str(search.pagum_to).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     to.append(date_to)
            # if search.ethiopian_to == False and search.pagum_to == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     to.append(today)

            # For initial date to widget Three

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


            try:
                data = {
                    'from': From[0],
                    'to': to[0],
                    'three': three[0],
                }
            except:
                data = {
                    'from': From,
                    'to': to,
                    'three': three,
                }     

           
            return data
    

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





