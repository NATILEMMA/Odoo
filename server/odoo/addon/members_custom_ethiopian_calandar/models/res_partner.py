
import random
import string
import werkzeug.urls

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


class SupportingMembers(models.Model):
    _inherit="supporter.members"


   
    becomes_a_candidate_on_ethiopian_date = fields.Date(string="In Ethiopian date")
  

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    vals['becomes_a_candidate_on'] = date1
                    vals['becomes_a_candidate_on_ethiopian_date'] = Edate1
                    pick1.clear()
       
        res = super(SupportingMembers, self).create(vals)
        try:
            if res.becomes_a_candidate_on:
                date1 = res.becomes_a_candidate_on
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                res.becomes_a_candidate_on_ethiopian_date = Edate1
        except:
            pass
        return res


    def write(self, vals):
        for record in self:
            _logger.info("############# Write:%s",vals)

            try:
                if vals['becomes_a_candidate_on'] is not None:
                    date_str = vals['becomes_a_candidate_on']
                    date_time_obj = date_str.split('-')                    
                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    vals['becomes_a_candidate_on_ethiopian_date'] = Edate
            except:
                pass
        
            # self.action_reload_page()
        return super(SupportingMembers, self).write(vals)


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
                    if models == "supporter.members":
                        if picked_date['pick'] == 1:
                            search.update({
                                'becomes_a_candidate_on': date_gr,
                                'becomes_a_candidate_on_ethiopian_date': date
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


class CandidateMembers(models.Model):
    _inherit = 'candidate.members'


   
    ethiopian_date = fields.Date(string="In Ethiopian date")
    ethiopian_date_of_becomes_member_on = fields.Date(string="In Ethiopian date")
  

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    vals['date'] = date1
                    vals['ethiopian_date'] = Edate1
                    pick1.clear()
                
        for i in range(0, len(pick2)):
            if i == (len(pick2)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick2[i]['pick'] == 2:
                    vals['becomes_member_on'] = date1
                    vals['ethiopian_date_of_becomes_member_on'] = Edate1
                    pick2.clear()

        res = super(CandidateMembers, self).create(vals)
        try:
            if res.date:
                date1 = res.date
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
                res.ethiopian_date = Edate1
        except:
            pass
       
        try:
            if res.becomes_member_on:
                date2 = res.becomes_member_on
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
                res.ethiopian_date_of_becomes_member_on = Edate2
        except:
            pass

        return res



    def write(self, vals):
        for record in self:
            _logger.info("############# Write:%s",vals)

            try:
                if vals['date'] is not None:
                    date_str = vals['date']
                    if type(vals['date']) == str:
                        date_time_obj = date_str.split('-')
                        today = date.today()
                        if today.month < int(date_time_obj[1]):
                            record.age = (today.year - int(date_time_obj[0])) - 1
                        else:
                            if today.month == int(date_time_obj[1]) and today.day < int(date_time_obj[2]):
                                record.age = (today.year - int(date_time_obj[0])) - 1
                            else:
                                record.age = today.year - int(date_time_obj[0])
                        Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                        vals['ethiopian_date'] = Edate
                    else:
                        date1 = vals['date']
                        today = date.today()
                        if today.month < date1.month:
                            record.age = (today.year - date1.year) - 1
                        else:
                            if today.month == date1.month and today.day < date1.day:
                                record.age = (today.year - date1.year) - 1
                            else:
                                record.age = today.year - date1.year                     
                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    vals['ethiopian_date'] = Edate
            except:
                pass
            try:
                if vals['becomes_member_on'] is not None:
                    date_str = vals['becomes_member_on']
                    date_time_obj = date_str.split('-')
                    Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                    vals['ethiopian_date_of_becomes_member_on'] = Edate
            except:
                pass
        
            # self.action_reload_page()
        return super(CandidateMembers, self).write(vals)


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
                    if models == "candidate.members":
                        if picked_date['pick'] == 1:
                            search.update({
                                'date': date_gr,
                                'ethiopian_date': date
                                })
                            search.action_reload_page()
                             

                        if picked_date['pick'] == 2:
                            search.update({
                                'becomes_member_on': date_gr,
                                'ethiopian_date_of_becomes_member_on':date
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
        if picked_date['pick'] == 4:
            pick3.append(data)






