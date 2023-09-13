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


all_days = {
            '0': 'Monday',
            '1': 'Tuesday',
            '2': 'Wednesday',
            '3': 'Thursday',
            '4': 'Friday',
            '5': 'Saturday',
            '6': 'Sunday'
            }


class VisitDetails(models.Model):
    _inherit = 'fo.visit'

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


        if vals.get('resource_calendar_id') == False:
            raise UserError(_("Please Add Working Days First"))


        date_new = False

        if not vals['from_portal']:
            if not vals.get('date'):
                date_new = self.date

            if type(vals.get('date')) == str:
                date_new = datetime.strptime(vals.get('date'), '%Y-%m-%d')
                if date_new.date() < date.today():
                    raise UserError(_("Please Add A Date After Today"))
            elif type(vals.get('date')) == date:
                date_new = vals.get('date')
                if date_new < date.today():
                    raise UserError(_("Please Add A Date After Today"))
            # else:
            #     date_new = vals.get('date').date()
            #     if date_new < date.today():
            #         raise UserError(_("Please Add A Date After Today"))

            days = False

            if vals.get('resource_calendar_id'):
                calendar = self.env['resource.calendar'].search([('id', '=', vals.get('resource_calendar_id'))])
                days = calendar.attendance_ids.mapped('dayofweek')
            else:
                days = self.resource_calendar_id.attendance_ids.mapped('dayofweek')


            new_list = []
            for day in days:
                new_list.append(all_days[day])

            if date_new.strftime("%A") not in new_list:
                raise UserError(_("The Date You Picked Isn't Apart of Your Working Days"))

            leaves = False

            if vals.get('resource_calendar_id'):
                calendar = self.env['resource.calendar'].search([('id', '=', vals.get('resource_calendar_id'))])
                leaves = calendar.global_leave_ids
            else:
                leaves = self.resource_calendar_id.global_leave_ids


            for leave in leaves:
                if type(date_new) == date:
                    if leave.date_from <= datetime(date_new.year, date_new.month, date_new.day) <= leave.date_to:
                        raise UserError(_("The Date You Picked Is A Holiday"))
                else:
                    if leave.date_from <= date_new <= leave.date_to:
                        raise UserError(_("The Date You Picked Is A Holiday"))


        res = super(VisitDetails, self).create(vals)
        if res.date:
            date1 = res.date
            Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)

            if type(Edate1) == date:
                res.ethiopian_from = Edate1

            elif type(Edate1) == str:
                res.pagum_from = Edate1
                res.is_pagum_from = False


        return res


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

        if vals.get('resource_calendar_id') == False:
            raise UserError(_("Please Add Working Days First"))


        date_new = False

        if type(vals.get('date')) == str:
            date_new = datetime.strptime(vals.get('date'), '%Y-%m-%d')
            if date_new.date() < date.today():
                raise UserError(_("Please Add A Date After Today"))
        if type(vals.get('date')) == date:
            date_new = vals.get('date')
            if date_new < date.today():
                raise UserError(_("Please Add A Date After Today"))
        if not vals.get('date'):
            date_new = self.date

        days = False

        if vals.get('resource_calendar_id'):
            calendar = self.env['resource.calendar'].search([('id', '=', vals.get('resource_calendar_id'))])
            days = calendar.attendance_ids.mapped('dayofweek')
        else:
            days = self.resource_calendar_id.attendance_ids.mapped('dayofweek')


        new_list = []
        for day in days:
            new_list.append(all_days[day])

        if date_new.strftime("%A") not in new_list:
            raise UserError(_("The Date You Picked Isn't Apart of Your Working Days"))

        leaves = False

        if vals.get('resource_calendar_id'):
            calendar = self.env['resource.calendar'].search([('id', '=', vals.get('resource_calendar_id'))])
            leaves = calendar.global_leave_ids
        else:
            leaves = self.resource_calendar_id.global_leave_ids


        for leave in leaves:
            if type(date_new) == date:
                if leave.date_from <= datetime(date_new.year, date_new.month, date_new.day) <= leave.date_to:
                    raise UserError(_("The Date You Picked Is A Holiday"))
            else:
                if leave.date_from <= date_new <= leave.date_to:
                    raise UserError(_("The Date You Picked Is A Holiday"))

        return super(VisitDetails, self).write(vals)



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
            if search.ethiopian_from != False and search.pagum_from == False:
                _logger.info("################# Both T")
                return {'from': search.ethiopian_from}
            elif search.ethiopian_from == False and search.pagum_from != False:
                _logger.info("################# Both T")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2] + '-' + date_from_str[0] + '-' + date_from_str[1]
                return {'from': date_from}
            elif search.ethiopian_from == False and search.pagum_from == False:
                _logger.info("################# From - f  To - true")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': today}
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


