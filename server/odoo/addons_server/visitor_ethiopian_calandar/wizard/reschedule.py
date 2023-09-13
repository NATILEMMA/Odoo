import random
import string
import werkzeug.urls
import pytz
from odoo import tools
from collections import defaultdict
from datetime import datetime, date, timedelta
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
from odoo.exceptions import UserError, ValidationError
from odoo.addons.s2u_online_appointment.helpers import functions

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

class RescheduleVisits(models.TransientModel):
    _inherit = "reschedule.visit"


    ethiopian_from = fields.Date(string="Date", store=True) # date
    pagum_from = fields.Char(string="Date", store=True)
    is_pagum_from = fields.Boolean(default='True', string="Date")


    def action_done(self):
        """This function will be the action for wizards"""
        if len(pick1) > 0:
            for i in range(0, len(pick1)):

                if i == (len(pick1) - 1):
                    date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'], pick1[i]['month'], pick1[i]['day'])
                    Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)
                    if pick1[i]['pick'] == 1:
                        if type(Edate1) == str:
                            self.ethiopian_from = None
                            self.date = date1
                            self.pagum_from = Edate1
                            self.is_pagum_from = False
                            pick1.clear()
                        if type(Edate1) == date:
                            self.date = date1
                            self.ethiopian_from = Edate1
                            pick1.clear()
        else:
            date1 = self.date
            Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)

            if type(Edate1) == date:
                self.ethiopian_from = Edate1

            elif type(Edate1) == str:
                self.pagum_from = Edate1
                self.is_pagum_from = False
  

        wizard = self.env['reschedule.visit'].search([('id', '=', self.id)])
        if self.check_in_float and self.duration_in_float and self.date:
            if self.date:
                days = wizard.visits_id.resource_calendar_id.attendance_ids.mapped('dayofweek')
                new_list = []
                for day in days:
                    new_list.append(all_days[day])
                if self.date.strftime("%A") not in new_list:
                    self.date = False
                    raise UserError(_("The Date You Picked Isn't Apart of Your Working Days"))
                leaves = wizard.visits_id.resource_calendar_id.global_leave_ids
                for leave in leaves:
                    if leave.date_from.date() <= self.date <= leave.date_to.date():
                        self.date = False
                        raise UserError(_("The Date You Picked Is A Holiday"))

            out = self.duration_in_float + self.check_in_float
            self.check_out_float = out
            if self.check_out_float > 11.0:
                raise UserError(_("Sorry, This Time is Out Of The Range of Regular Working Hours"))
            else:
                self.env['rescheduled.time'].sudo().create({
                    'date': wizard.visits_id.date,
                    'ethiopian_from': wizard.visits_id.ethiopian_from,
                    'pagum_from': wizard.visits_id.pagum_from,
                    'is_pagum_from': wizard.visits_id.is_pagum_from,
                    'check_in_float': wizard.visits_id.check_in_float,
                    'check_out_float': wizard.visits_id.check_out_float,
                    'duration_in_float': wizard.visits_id.duration_in_float,
                    'visits_id': wizard.visits_id.id
                })

                ethTZ = pytz.timezone("Africa/Addis_Ababa")
                date_app = self.date.strftime("%Y-%m-%d")
                start = date_app + " " + functions.float_to_time(self.check_in_float)
                date_start = self.ld_to_utc(start)

                if wizard.visits_id.state == 'draft':
                    wizard.visits_id.write({
                        'state': 'approved',
                        'date': self.date,
                        'ethiopian_from': self.ethiopian_from,
                        'pagum_from': self.pagum_from,
                        'is_pagum_from': self.is_pagum_from,
                        'check_in_float': self.check_in_float,
                        'duration_in_float': self.duration_in_float,
                        'check_out_float': self.check_out_float,
                        'rescheduled': True
                    })
                    wizard.visits_id.event_id.write({
                        'start': date_start.strftime("%Y-%m-%d %H:%M"),
                        'stop': (date_start + timedelta(minutes=round(self.duration_in_float * 60))).strftime("%Y-%m-%d %H:%M"),
                        'duration': self.duration_in_float
                    })
                    wizard.visits_id.event_id.attendee_ids.write({
                        'state': 'accepted'
                    })
                    registration = self.env['s2u.appointment.registration'].search([('event_id', '=', wizard.visits_id.event_id.id)])
                    if registration:
                        registration.state = 'valid'
                    mail_temp = self.env.ref('visitor_gate_management.appointment_rescheduled_in')
                    mail_temp.send_mail(wizard.visits_id.id)
                    self.env.user.notify_success("Visit Has Been Successfully Rescheduled", '<h4>Meeting Rescheduled</h4>', True)
                    wizard.visits_id.deactivate_activity(wizard.visits_id)

                if wizard.visits_id.state == 'check_in':
                    appointment = self.env['calendar.event'].sudo().with_context(detaching=True).create({
                        'name': "Visits",
                        'description': wizard.visits_id.event_id.description,
                        'start': date_start.strftime("%Y-%m-%d %H:%M"),
                        'stop': (date_start + timedelta(minutes=round(self.duration_in_float * 60))).strftime("%Y-%m-%d %H:%M"),
                        'duration': self.duration_in_float,
                        'partner_ids': wizard.visits_id.event_id.partner_ids.ids
                    })
                    appointment.attendee_ids.write({
                        'state': 'accepted'
                    })
                    visit = self.env['fo.visit'].create({
                        'visitor': [[6, 0, wizard.visits_id.visitor.ids]],
                        'reason': wizard.visits_id.reason.id,
                        'visit_with': wizard.visits_id.visit_with,
                        'department': wizard.visits_id.department.id,
                        'visiting_employee': wizard.visits_id.visiting_employee.ids,
                        'state': 'approved',
                        'disappear_approve': wizard.visits_id.disappear_approve,
                        'resource_calendar_id': wizard.visits_id.resource_calendar_id.id,
                        'event_id':  appointment.id,
                        'meeting_minute': wizard.visits_id.meeting_minute,
                        'date': self.date,
                        'ethiopian_from': self.ethiopian_from,
                        'pagum_from': self.pagum_from,
                        'is_pagum_from': self.is_pagum_from,
                        'check_in_float': self.check_in_float,
                        'duration_in_float': self.duration_in_float,
                        'check_out_float': self.check_out_float,
                        'rescheduled': True
                    })
                    rescheduled = self.env['rescheduled.time'].create({
                        'date': wizard.visits_id.date,
                        'ethiopian_from': wizard.visits_id.ethiopian_from,
                        'pagum_from': wizard.visits_id.pagum_from,
                        'is_pagum_from': wizard.visits_id.is_pagum_from,
                        'check_in_float': wizard.visits_id.check_in_float,
                        'check_out_float': wizard.visits_id.check_out_float,
                        'duration_in_float': wizard.visits_id.duration_in_float,
                        'visits_id': visit.id
                    })
                    mail_temp = self.env.ref('visitor_gate_management.appointment_accepted_in')
                    mail_temp.send_mail(visit.id)
                    self.env.user.notify_success("Visit Has Been Successfully Rescheduled", '<h4>Meeting Rescheduled</h4>', True)
        else:
            raise UserError(_("Please Fill In The Required Fields"))



    @api.model
    def initial_date(self, data):
        pass



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

