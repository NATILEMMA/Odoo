# -*- coding: utf-8 -*-

import pytz
from datetime import date, datetime
import datetime
import base64
from odoo.addons.s2u_online_appointment.helpers import functions # This one is assumed from core module
# from .helpers import functions

from odoo import http, modules, tools
from odoo import api, fields as odoo_fields, models, _, SUPERUSER_ID
from odoo.http import request
import logging
import math
import re
from odoo.addons.portal.controllers.portal import pager as portal_pager
from werkzeug import urls
from ethiopian_date import EthiopianDateConverter
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class OnlineAppointment(http.Controller):


    def ld_to_utc(self, ld, appointee_id, duration=False):

        date_parsed = datetime.datetime.strptime(ld, "%Y-%m-%d  %H:%M")
        if duration:
            date_parsed += datetime.timedelta(hours=duration)

        user = request.env['hr.employee'].sudo().search([('id', '=', appointee_id)])
        if user:
            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            local = ethTZ
            local_dt = local.localize(date_parsed, is_dst=None)
            return local_dt.astimezone(pytz.utc)
        else:
            return ld



    def appointee_id_to_partner_id(self, appointee_id):

        appointee = request.env['hr.employee'].sudo().search([('id', '=', appointee_id)])
        partner = request.env['res.partner'].sudo().search([('id', '=', appointee.user_partner_id.id)])
        if appointee:
            # return appointee.partner_id.id
            return partner.id
        else:
            return False

    def select_appointees(self, criteria='default', appointment_option=False):

        if not appointment_option:
            return []

        if appointment_option.user_specific:
            user_allowed_ids = appointment_option.users_allowed.ids
            slots = request.env['s2u.appointment.slot'].sudo().search([('user_id', 'in', user_allowed_ids)])
            appointee_ids = [s.user_id.id for s in slots]
        else:
            slots = request.env['s2u.appointment.slot'].sudo().search([])
            appointee_ids = [s.user_id.id for s in slots]
        appointee_ids = list(set(appointee_ids))
        return appointee_ids

    def select_options(self, criteria='default'):

        return request.env['s2u.appointment.option'].sudo().search([('state', '=', 'approved')])

    def prepare_values(self, form_data=False, default_appointee_id=False, criteria='default'):

        appointee_ids = self.select_appointees(criteria=criteria)
        options = self.select_options(criteria=criteria)

        partner = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner.id)])
        is_users = []
        is_member = False
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")

        if partner.is_league == True or partner.is_member == True or partner.is_leader == True:
            is_member = True

        values = {
            'appointees': request.env['hr.employee'].sudo().search([('id', 'in', appointee_ids)]),
            'appointment_options': options,
            'timeslots': [],
            'appointee_id': 0,
            'appointment_option_id': 0,
            'appointment_date': '',
            'timeslot_id': 0,
            'mode': 'public' if request.env.user._is_public() else 'registered',
            'name': request.env.user.partner_id.name if not request.env.user._is_public() else '',
            'email': request.env.user.partner_id.email if not request.env.user._is_public() else '',
            'city_id': request.env.user.partner_id.city_id.id if not request.env.user._is_public() else '',
            'subcity': request.env.user.partner_id.subcity.id if not request.env.user._is_public() else '',
            'phone': request.env.user.partner_id.phone if not request.env.user._is_public() else '',
            'regions': request.env['res.country.state'].sudo().search([('country_id', '=', 69)]),
            'subcities': request.env['res.state.subcity'].sudo().search([]),
            'remarks': '',
            'error': {},
            'error_message': [],
            'form_action': '/online-appointment/appointment-confirm',
            'form_criteria': criteria,
            'is_member': is_member,
            'users': users,
            'is_users': is_users 
        }

        if form_data:
            try:
                appointee_id = int(form_data.get('appointee_id', 0))
            except:
                appointee_id = 0

            try:
                appointment_option_id = int(form_data.get('appointment_option_id', 0))
            except:
                appointment_option_id = 0

            try:
                timeslot_id = int(form_data.get('timeslot_id', 0))
            except:
                timeslot_id = 0

            try:
                appointment_date = datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').strftime('%d/%m/%Y')
            except:
                appointment_date = ''

            values.update({
                'name': form_data.get('name', ''),
                'email': form_data.get('email', ''),
                'phone': form_data.get('phone', ''),
                'city_id': int(form_data.get('city_id', 0)),
                'subcity': int(form_data.get('subcity', 0)),
                'appointee_id': appointee_id,
                'appointment_option_id': appointment_option_id,
                'appointment_date': appointment_date,
                'timeslot_id': timeslot_id,
                'remarks': form_data.get('remarks', '')
            })

            if appointee_id and appointment_option_id and appointment_date:
                free_slots = self.get_free_appointment_slots_for_day(appointment_option_id, form_data['appointment_date'], appointee_id, criteria)
                days_with_free_slots = self.get_days_with_free_slots(appointment_option_id,
                                                                     appointee_id,
                                                                     datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').year,
                                                                     datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').month,
                                                                     criteria)
                values.update({
                    'timeslots': free_slots,
                    'days_with_free_slots': days_with_free_slots,
                    'focus_year': datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').year,
                    'focus_month': datetime.datetime.strptime(form_data['appointment_date'], '%d/%m/%Y').month
                })
        else:
            if values['appointees']:
                try:
                    default_appointee_id = int(default_appointee_id)
                except:
                    default_appointee_id = False
                if default_appointee_id and default_appointee_id in values['appointees'].ids:
                    values['appointee_id'] = default_appointee_id
                else:
                    values['appointee_id'] = values['appointees'][0].id
            if options:
                values['appointment_option_id'] = options[0].id
        return values

    @http.route(['/online-appointment'], auth='public', website=True, csrf=True)
    def online_appointment(self, **kw):
        
        values = self.prepare_values(default_appointee_id=kw.get('appointee', False))
        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('dashboard_member12.only_registered_users', values)

        return request.render('dashboard_member12.make_appointment', values)

    @http.route(['/online-appointment/appointment-confirm'], auth="public", type='http', website=True)
    def online_appointment_confirm(self, **post):
        error = {}
        error_message = []

        val = {}
        partner = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner.id)])
        is_users = []
        is_member = False
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")

        if partner.is_league == True or partner.is_member == True or partner.is_leader == True:
            is_member = True

        val['is_member'] = is_member
        val['is_users'] = is_users
        val['users'] = users

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('dashboard_member12.only_registered_users', val)

            if not post.get('name', False):
                error['name'] = True
                error_message.append(_('Please enter your name.'))
            if not post.get('email', False):
                error['email'] = True
                error_message.append(_('Please enter your email address.'))
            elif not functions.valid_email(post.get('email', '')):
                error['email'] = True
                error_message.append(_('Please enter a valid email address.'))
            if not post.get('city_id', False):
                error['city_id'] = True
                error_message.append(_('Please enter your City address.'))
            if not post.get('subcity', False):
                error['subcity'] = True
                error_message.append(_('Please enter your Sub City address.'))
            if not post.get('phone', False):
                error['phone'] = True
                error_message.append(_('Please enter your phonenumber.'))

        try:
            appointee_id = int(post.get('appointee_id', 0))
        except:
            appointee_id = 0
        if not appointee_id:
            error['appointee_id'] = True
            error_message.append(_('Please select a valid appointee.'))

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', int(post.get('appointment_option_id', 0)))])
        if not option:
            error['appointment_option_id'] = True
            error_message.append(_('Please select a valid subject.'))
        slot = request.env['s2u.appointment.slot'].sudo().search([('id', '=', int(post.get('timeslot_id', 0)))])
        if not slot:
            error['timeslot_id'] = True
            error_message.append(_('Please select a valid timeslot.'))

        try:
            date_start = datetime.datetime.strptime(post['appointment_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            day_slot = date_start + ' ' + functions.float_to_time(slot.slot_start)
            start_datetime = self.ld_to_utc(day_slot, appointee_id)
            floats = option.duration + slot.slot_start
            time_out = date_start + " " + functions.float_to_time(floats)
        except:
            error['appointment_date'] = True
            error_message.append(_('Please select a valid date.'))

        values = self.prepare_values(form_data=post)
        if error_message:
            values['error'] = error
            values['error_message'] = error_message
            return request.render('dashboard_member12.make_appointment', values)

        if not self.check_slot_is_possible(option.id, post['appointment_date'], appointee_id, slot.id):
            values['error'] = {'timeslot_id': True}
            values['error_message'] = [_('Slot is already occupied, please choose another slot.')]
            return request.render('dashboard_member12.make_appointment', values)

        if request.env.user._is_public():
            partner = request.env['res.partner'].sudo().search(['|', ('phone', 'ilike', values['phone']),
                                                                     ('email', 'ilike', values['email'])])
            if partner:
                partner.write({
                    'phone': values['phone'],
                    'email': values['email'],
                    'city_id': int(values['city_id']),
                    'subcity': int(values['subcity']),
                })
                partner_ids = [self.appointee_id_to_partner_id(appointee_id), partner.id]
            # else:
            #     partner = request.env['res.partner'].sudo().create({
            #         'name': values['name'],
            #         'phone': values['phone'],
            #         'email_address': values['email_address'],
            #         'region': int(values['region']),
            #         'subcity': int(values['subcity']),
            #     })
            #     partner_ids = [self.appointee_id_to_partner_id(appointee_id), partner.id]
        else:
            request.env.user.partner_id.write({
                    'phone': values['phone'],
                    'email': values['email'],
                    'city_id': int(values['city_id']),
                    'subcity': int(values['subcity']),
                })
            partner_ids = [self.appointee_id_to_partner_id(appointee_id), request.env.user.partner_id.id]

        # set detaching = True, we do not want to send a mail to the attendees
        appointment = request.env['calendar.event'].sudo().with_context(detaching=True).create({
            'name': option.name,
            'description': post.get('remarks', ''),
            'start': start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            'stop': (start_datetime + datetime.timedelta(minutes=round(option.duration * 60))).strftime("%Y-%m-%d %H:%M:%S"),
            'duration': option.duration,
            'partner_ids': [(6, 0, partner_ids)]
        })
        # set all attendees on 'accepted'
        appointment.attendee_ids.write({
            'state': 'tentative'
        })
        # registered user, we want something to show in his portal
        if not request.env.user._is_public():
            vals = {
                'partner_id': request.env.user.partner_id.id,
                'appointee_id': self.appointee_id_to_partner_id(appointee_id),
                'event_id': appointment.id,
                'state': 'pending'
            }
            registration = request.env['s2u.appointment.registration'].create(vals)

            vals.update(
                {
                    'post': post,
                    'option': option,
                    'check_in_date': date_start,
                    'check_in_time': functions.float_to_time(slot.slot_start),
                    'check_out_time': functions.float_to_time(floats),
                    'event_id': appointment.id,
                    'appointee_id': appointee_id
                }
            )

            if post['phone']:
                for st in post['phone']:
                    if not st.isdigit():
                        return request.render('dashboard_member12.character_in_phone')
                if post['phone'][0] != '0':
                    return request.render('dashboard_member12.zero_in_phone')
                if len(post['phone']) != 10:
                    return request.render('dashboard_member12.ten_digit_phone')


            date_now = datetime.datetime.strptime(vals['check_in_date'], '%Y-%m-%d')

            leaves = request.env['resource.calendar'].search([('name', '=', 'Standard 40 hours/week')]).global_leave_ids
            for leave in leaves:
                if leave.date_from <= date_now <= leave.date_to:
                    return request.render('dashboard_member12.date_holiday')

            self.sync_with_gate_visitor(vals)

        return request.redirect('/online-appointment/appointment-scheduled?appointment=%d' % appointment.id)

    def sync_with_gate_visitor(self, data=False):
        partner_info = request.env['res.partner'].sudo().search([('id', '=' ,data['partner_id'])], limit=1)
        _logger.info('\n  info: %s', str(partner_info['phone']))
        fo_visitor_user = None

        reason = request.env['fo.purpose'].sudo().search([('name', 'like', data['option'].name)], limit=1)
        if not reason:
            reason = request.env['fo.purpose'].sudo().create({
                'name': data['option'].name
            })

        check_in = functions.time_to_float(data['check_in_time'])
        check_out = functions.time_to_float(data['check_out_time'])
        date_now = datetime.datetime.strptime(data['check_in_date'], '%Y-%m-%d')
        fo_visit_vals = {
            'visitor': [[6, 0, [data['partner_id']]]],
            'phone': data['post']['phone'],
            'email':data['post']['email'],
            'reason': reason.id,
            'date': date_now,
            'visit_with': 'employee',
            'disappear_approve': True,
            'check_in_float': check_in,
            'duration_in_float': data['option']['duration'],
            'check_out_float': check_out,
            'visiting_employee': [[6, 0, [data['appointee_id']]]],
            'state': 'draft',
            'event_id': data['event_id'],
            'from_portal': True
        }

    
        fo_visit = request.env['fo.visit'].sudo().create(fo_visit_vals)

    @http.route(['/online-appointment/appointment-scheduled'], auth="public", type='http', website=True)
    def confirmed(self, **post):

        values = {}
        partner = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner.id)])
        is_users = []
        is_member = False
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")

        if partner.is_league == True or partner.is_member == True or partner.is_leader == True:
            is_member = True

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('dashboard_member12.only_registered_users', values)

        appointment = request.env['calendar.event'].sudo().search([('id', '=', int(post.get('appointment', 0)))])
        if not appointment:
            values = {
                'appointment': False,
                'error_message': [_('Appointment not found.')]
            }
            values['is_member'] = is_member
            values['is_users'] = is_users
            values['users'] = users
            return request.render('dashboard_member12.thanks', values)

        if request.env.user._is_public():
            values = {
                'appointment': False,
                'error_message': []
            }
            values['is_member'] = is_member
            values['is_users'] = is_users
            values['users'] = users
            return request.render('dashboard_member12.thanks', values)
        else:
            if request.env.user.partner_id.id not in appointment.partner_ids.ids:
                values = {
                    'appointment': False,
                    'error_message': [_('Appointment not found.')]
                }
                values['is_member'] = is_member
                values['is_users'] = is_users
                values['users'] = users
                return request.render('dashboard_member12.thanks', values)

            values = {
                'appointment': appointment,
                'error_message': []
            }
            values['is_member'] = is_member
            values['is_users'] = is_users
            values['users'] = users
            return request.render('dashboard_member12.thanks', values)

    def recurrent_events_overlapping(self, appointee_id, event_start, event_stop):
        query = """
                    SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                        WHERE ep.res_partner_id = %s AND
                              e.active = true AND
                              e.recurrency = true AND
                              e.final_date >= %s AND
                              e.id = ep.calendar_event_id                                         
        """
        request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                       datetime.datetime.now().strftime('%Y-%m-%d')))
        res = request.env.cr.fetchall()
        event_ids = [r[0] for r in res]
        for event in request.env['calendar.event'].sudo().browse(event_ids):
            recurrent_dates = event._get_recurrent_dates_by_event()
            for recurrent_start_date, recurrent_stop_date in recurrent_dates:
                recurrent_start_date_short = recurrent_start_date.strftime('%Y-%m-%d %H:%M')
                recurrent_stop_date_short = recurrent_stop_date.strftime('%Y-%m-%d %H:%M')
                if (event_start <= recurrent_start_date_short <= event_stop) or (
                        recurrent_start_date_short <= event_start and recurrent_stop_date_short >= event_stop) or (
                        event_start <= recurrent_stop_date_short <= event_stop):
                    return True
        return False

    def check_slot_is_possible(self, option_id, appointment_date, appointee_id, slot_id):

        if not appointment_date:
            return False

        if not appointee_id:
            return False

        if not option_id:
            return False

        if not slot_id:
            return False

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', option_id)])
        if not option:
            return False
        slot = request.env['s2u.appointment.slot'].sudo().search([('id', '=', slot_id)])
        if not slot:
            return False

        date_start = datetime.datetime.strptime(appointment_date, '%d/%m/%Y').strftime('%Y-%m-%d')

        # if today, then skip slots in te past (< current time)
        if date_start == datetime.datetime.now().strftime('%Y-%m-%d') and self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot_start), appointee_id) < datetime.datetime.now(pytz.utc):
            return False

        event_start = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot_start), appointee_id).strftime("%Y-%m-%d %H:%M:%S")
        event_stop = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot.slot_start), appointee_id,
                                    duration=option.duration).strftime("%Y-%m-%d %H:%M:%S")

        query = """
                SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                    WHERE ep.res_partner_id = %s AND
                          e.active = true AND
                          (e.recurrency = false or e.recurrency is null) AND
                          e.id = ep.calendar_event_id AND 
                        ((e.start >= %s AND e.start <= %s) OR
                             (e.start <= %s AND e.stop >= %s) OR
                             (e.stop > %s) AND e.stop <= %s)                                       
        """
        request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                       event_start, event_stop,
                                       event_start, event_stop,
                                       event_start, event_stop))
        res = request.env.cr.fetchall()
        if not res:
            if not self.recurrent_events_overlapping(appointee_id, event_start, event_stop):
                return True

        return False

    def filter_slots(self, slots, criteria):
        # override this method when slots needs to be filtered
        return slots

    def get_free_appointment_slots_for_day(self, option_id, appointment_date, appointee_id, criteria):

        def slot_present(slots, slot):

            for s in slots:
                if s['timeslot'] == functions.float_to_time(slot):
                    return True
            return False

        if not appointment_date:
            return []

        if not appointee_id:
            return []

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', option_id)])
        if not option:
            return []

        week_day = datetime.datetime.strptime(appointment_date, '%d/%m/%Y').weekday()
        slots = request.env['s2u.appointment.slot'].sudo().search([('user_id', '=', appointee_id),
                                                                   ('day', '=', str(week_day))])
        slots = self.filter_slots(slots, criteria)

        date_start = datetime.datetime.strptime(appointment_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        free_slots = []


        looped_slots = []
        for slot in slots:
            current = slot.slot_start
            looped_slots.append({
                'id': slot.id,
                'slot': current
            })

            while (current + option.duration) < slot.slot_end:
                current += option.duration
                looped_slots.append({
                    'id': slot.id,
                    'slot': current
                })                

        for i in range(len(looped_slots)): 
            for j in range(i + 1, len(looped_slots)): 
                if looped_slots[i]['slot'] > looped_slots[j]['slot']: 
                    looped_slots[i], looped_slots[j] = looped_slots[j], looped_slots[i] 


        for slot in looped_slots:
            # skip double slots
            if slot_present(free_slots, slot['slot']):
                continue

            # if today, then skip slots in te past (< current time)
            if date_start == datetime.datetime.now().strftime('%Y-%m-%d') and self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot['slot']), appointee_id) < datetime.datetime.now(pytz.utc):
                continue

            event_start = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot['slot']), appointee_id).strftime("%Y-%m-%d %H:%M:%S")
            event_stop = self.ld_to_utc(date_start + ' ' + functions.float_to_time(slot['slot']), appointee_id,
                                        duration=option.duration).strftime("%Y-%m-%d %H:%M:%S")

            # check normal calendar events
            query = """
                    SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                        WHERE ep.res_partner_id = %s AND
                              e.active = true AND
                              (e.recurrency = false or e.recurrency is null) AND 
                              e.id = ep.calendar_event_id AND 
                            ((e.start >= %s AND e.start <= %s) OR
                             (e.start <= %s AND e.stop >= %s) OR
                             (e.stop > %s) AND e.stop <= %s)                                         
            """
            request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                           event_start, event_stop,
                                           event_start, event_stop,
                                           event_start, event_stop))
            res = request.env.cr.fetchall()
            if not res:
                if not self.recurrent_events_overlapping(appointee_id, event_start, event_stop):
                    free_slots.append({
                        'id': slot['id'],
                        'timeslot': functions.float_to_time(slot['slot'])
                    })

        return free_slots

    def get_days_with_free_slots(self, option_id, appointee_id, year, month, criteria):

        if not option_id:
            return {}

        if not appointee_id:
            return {}

        start_datetimes = {}
        start_date = datetime.date(year, month, 1)
        for i in range(31):
            if start_date < datetime.date.today():
                start_date += datetime.timedelta(days=1)
                continue
            if start_date.weekday() not in start_datetimes:
                start_datetimes[start_date.weekday()] = []
            start_datetimes[start_date.weekday()].append(start_date.strftime('%Y-%m-%d'))
            start_date += datetime.timedelta(days=1)
            if start_date.month != month:
                break

        day_slots = []

        option = request.env['s2u.appointment.option'].sudo().search([('id', '=', option_id)])
        if not option:
            return {}

        for weekday, dates in start_datetimes.items():
            slots = request.env['s2u.appointment.slot'].sudo().search([('user_id', '=', appointee_id),
                                                                       ('day', '=', str(weekday))])
            slots = self.filter_slots(slots, criteria)

            for slot in slots:
                for d in dates:
                    # if d == today, then skip slots in te past (< current time)
                    if d == datetime.datetime.now().strftime('%Y-%m-%d') and self.ld_to_utc(d + ' ' + functions.float_to_time(slot.slot_start), appointee_id) < datetime.datetime.now(pytz.utc):
                        continue

                    day_slots.append({
                        'timeslot': functions.float_to_time(slot.slot_start),
                        'date': d,
                        'start': self.ld_to_utc(d + ' ' + functions.float_to_time(slot.slot_start), appointee_id).strftime("%Y-%m-%d %H:%M:%S"),
                        'stop': self.ld_to_utc(d + ' ' + functions.float_to_time(slot.slot_start), appointee_id, duration=option.duration).strftime("%Y-%m-%d %H:%M:%S")
                    })
        days_with_free_slots = {}
        for d in day_slots:
            if d['date'] in days_with_free_slots:
                # this day is possible, there was a slot possible so skip other slot calculations for this day
                # We only need to inform the visitor he can click on this day (green), after that he needs to
                # select a valid slot.
                continue

            query = """
                    SELECT e.id FROM calendar_event e, calendar_event_res_partner_rel ep  
                        WHERE ep.res_partner_id = %s AND 
                              e.active = true AND
                              (e.recurrency = false or e.recurrency is null) AND
                              e.id = ep.calendar_event_id AND  
                            ((e.start >= %s AND e.start <= %s) OR
                             (e.start <= %s AND e.stop >= %s) OR
                             (e.stop > %s) AND e.stop <= %s)                                         
            """
            request.env.cr.execute(query, (self.appointee_id_to_partner_id(appointee_id),
                                           d['start'], d['stop'],
                                           d['start'], d['stop'],
                                           d['start'], d['stop']))
            res = request.env.cr.fetchall()
            if not res:
                if not self.recurrent_events_overlapping(appointee_id, d['start'], d['stop']):
                    days_with_free_slots[d['date']] = True
        return days_with_free_slots

    @http.route('/online-appointment/timeslots', type='json', auth='public', website=True)
    def free_timeslots(self, appointment_option, appointment_with, appointment_date, form_criteria, **kwargs):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return {
                    'timeslots': [],
                    'appointees': [],
                    'appointment_with': 0,
                    'days_with_free_slots': {},
                    'focus_year': 0,
                    'focus_month': 0,
                }

        try:
            option_id = int(appointment_option)
        except:
            option_id = 0
        try:
            appointee_id = int(appointment_with)
        except:
            appointee_id = 0
        try:
            date_parsed = datetime.datetime.strptime(appointment_date, '%d/%m/%Y')
        except:
            date_parsed = datetime.date.today()

        if option_id:
            option = request.env['s2u.appointment.option'].sudo().browse(option_id)
            appointee_ids = self.select_appointees(criteria=form_criteria, appointment_option=option)
            appointees = []
            for a in request.env['hr.employee'].sudo().search([('id', 'in', appointee_ids)]):
                appointees.append({
                    'id': a.id,
                    'name': a.name
                })
        else:
            appointees = []

        free_slots = self.get_free_appointment_slots_for_day(option_id, appointment_date, appointee_id, form_criteria)
        days_with_free_slots = self.get_days_with_free_slots(option_id,
                                                             appointee_id,
                                                             date_parsed.year,
                                                             date_parsed.month,
                                                             form_criteria)
        return {
            'timeslots': free_slots,
            'appointees': appointees,
            'appointment_with': appointee_id,
            'days_with_free_slots': days_with_free_slots,
            'focus_year': date_parsed.year,
            'focus_month': date_parsed.month,
        }

    @http.route('/online-appointment/month-bookable', type='json', auth='public', website=True)
    def month_bookable(self, appointment_option, appointment_with, appointment_year, appointment_month, form_criteria, **kwargs):

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return {
                    'days_with_free_slots': [],
                    'focus_year': 0,
                    'focus_month': 0,
                }

        try:
            option_id = int(appointment_option)
        except:
            option_id = 0
        try:
            appointee_id = int(appointment_with)
        except:
            appointee_id = 0
        try:
            appointment_year = int(appointment_year)
            appointment_month = int(appointment_month)
        except:
            appointment_year = 0
            appointment_month = 0

        if not appointment_year or not appointment_month:
            appointment_year = datetime.date.today().year
            appointment_month = datetime.date.today().month

        days_with_free_slots = self.get_days_with_free_slots(option_id,
                                                             appointee_id,
                                                             appointment_year,
                                                             appointment_month,
                                                             form_criteria)

        return {
            'days_with_free_slots': days_with_free_slots,
            'focus_year': appointment_year,
            'focus_month': appointment_month,
        }

    def online_appointment_state_change(self, appointment, previous_state):
        # method to override when  you want something to happen on state change, for example send mail
        return True

    @http.route(['/online-appointment/portal/cancel'], auth="public", type='http', website=True)
    def online_appointment_portal_cancel(self, **post):

        values = {}
        partner = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner.id)])
        is_users = []
        is_member = False
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")

        if partner.is_league == True or partner.is_member == True or partner.is_leader == True:
            is_member = True

        values['is_member'] = is_member
        values['is_users'] = is_users
        values['users'] = users

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('dashboard_member12.only_registered_users', values)

        try:
            id = int(post.get('appointment_to_cancel', 0))
        except:
            id = 0

        if id:
            appointment = request.env['s2u.appointment.registration'].search([('id', '=', id)])
            if appointment and (
                    appointment.partner_id == request.env.user.partner_id or appointment.appointee_id == request.env.user.partner_id):
                previous_state = appointment.state
                appointment.cancel_appointment()
                self.online_appointment_state_change(appointment, previous_state)

        return request.redirect('/my/online-appointments')

    @http.route(['/online-appointment/portal/confirm'], auth="public", type='http', website=True)
    def online_appointment_portal_confirm(self, **post):

        values = {}
        partner = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner.id)])
        is_users = []
        is_member = False
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")

        if partner.is_league == True or partner.is_member == True or partner.is_leader == True:
            is_member = True

        values['is_member'] = is_member
        values['is_users'] = is_users
        values['users'] = users

        if request.env.user._is_public():
            param = request.env['ir.config_parameter'].sudo().search([('key', '=', 's2u_online_appointment')], limit=1)
            if not param or param.value.lower() != 'public':
                return request.render('dashboard_member12.only_registered_users', values)

        try:
            id = int(post.get('appointment_to_confirm', 0))
        except:
            id = 0

        if id:
            appointment = request.env['s2u.appointment.registration'].search([('id', '=', id)])
            if appointment and (
                    appointment.partner_id == request.env.user.partner_id or appointment.appointee_id == request.env.user.partner_id):
                previous_state = appointment.state
                appointment.confirm_appointment()
                self.online_appointment_state_change(appointment, previous_state)

        return request.redirect('/my/online-appointments')


    @http.route('/registrations', type='http', auth='public', website=True)
    def register(self, **post):
        """This function will create supporters from portal"""
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        is_users = []
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")
        if post and request.httprequest.method == 'POST':
            values = {}
            values.update(post)
            for field in set(['residential_subcity_id', 'residential_wereda_id', 'ethnic_group', 'education_level', 'field_of_study_id']) & set(values.keys()):
                try:
                    values[field] = int(values[field])
                except:
                    values[field] = False
            values.pop('livelihood')

            year = request.env['fiscal.year'].search([('state', '=', 'active')])
            if not year:
                return request.render('dashboard_member12.year_error', {'is_users': is_users})
            plan_city = request.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
            if not plan_city:
                return request.render('dashboard_member12.plan_city_error', {'is_users': is_users})
            plan_subcity = request.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('subcity_id', '=', values['residential_subcity_id'])])
            if not plan_subcity:
                return request.render('dashboard_member12.plan_sub_city_error', {'is_users': is_users}) 
            plan_woreda = request.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('wereda_id', '=', values['residential_wereda_id'])])
            if not plan_woreda:
                return request.render('dashboard_member12.plan_wereda_error', {'is_users': is_users})

            if values['user_input']:
                request.env['user.input'].sudo().create({
                    'model': "Field of Study",
                    'user_input': values['user_input']
                })
                values['is_user_input'] = 'True'


            dob_eth_str = values['ethiopian_from']
            try:
                values['ethiopian_from'] = datetime.datetime.strptime(dob_eth_str, '%Y/%m/%d').date()
                values['date'] = EthiopianDateConverter.to_gregorian(values['ethiopian_from'].year, values['ethiopian_from'].month, values['ethiopian_from'].day)
            except ValueError as err:
                eth_str = dob_eth_str.split('/')
                values['date'] = EthiopianDateConverter.to_gregorian(int(eth_str[2]), int(eth_str[0]),
                                                              int(eth_str[1]))
                values['ethiopian_from'] = EthiopianDateConverter.to_ethiopian(values['date'].year, values['date'].month, values['date'].day)
                if type(values['ethiopian_from']) == date:
                    values['pagum_from'] = False
                    values['is_pagum_from'] = True
                if type(values['ethiopian_from']) == str:
                    values['pagum_from'] = values['ethiopian_from']
                    values['ethiopian_from'] = False
                    values['is_pagum_from'] = False


            today = date.today()
            dob = values['date']
            if dob >= today:
                return request.render('dashboard_member12.before_today', {'is_users': is_users})

            age_limit = request.env['age.range'].search([('for_which_stage', '=', 'supporter')])

            if today.month < dob.month:
                values['age'] = (today.year - dob.year) - 1
                if values['age'] < age_limit.minimum_age_allowed or values['age'] > age_limit.maximum_age_allowed:
                    return request.render('dashboard_member12.age_limit', {'is_users': is_users})
            else:
                if today.month == dob.month and today.day < dob.day:
                    values['age'] = (today.year - dob.year) - 1
                    if values['age'] < age_limit.minimum_age_allowed or values['age'] > age_limit.maximum_age_allowed:
                        return request.render('dashboard_member12.age_limit', {'is_users': is_users})
                else:
                    values['age']  = today.year - dob.year
                    if values['age'] < age_limit.minimum_age_allowed or values['age'] > age_limit.maximum_age_allowed:
                        return request.render('dashboard_member12.age_limit', {'is_users': is_users})

            if values['phone']:
                for st in values['phone']:
                    if not st.isdigit():
                        return request.render('dashboard_member12.character_in_phone', {'is_users': is_users})
                if values['phone'][0] != '0':
                    return request.render('dashboard_member12.zero_in_phone', {'is_users': is_users})
                if len(values['phone']) != 10:
                    return request.render('dashboard_member12.ten_digit_phone', {'is_users': is_users})

            values['name'] = values['first_name'] + " " + values['father_name'] + " " + values['grand_father_name']

            values['subcity_id'] = values['residential_subcity_id']
            values['wereda_id'] = values['residential_wereda_id']
            values['state'] = 'draft'


            exists = request.env['supporter.members'].search([('name', '=', values['name']), ('gender', '=', values['gender']), ('phone', '=', values['phone']), ('date', '=', values['date'])])
            if exists:
                return request.render('dashboard_member12.duplicate', {'is_users': is_users})
            phone_exists = request.env['supporter.members'].search([('phone', '=', values['phone'])])
            if phone_exists:
                return request.render('dashboard_member12.phone_duplicate', {'is_users': is_users})

            if values['image_1920']:
                values['image_1920'] = values['image_1920'].read()
                values['image_1920'] = base64.b64encode(values['image_1920'])
                values['work_place'] = values['company_name']
                values.pop('company_name')
                return request.render('dashboard_member12.registration_end')                                       
            else:
                values['work_place'] = values['company_name']
                values.pop('company_name')
                request.env['supporter.members'].sudo().create(values)
                return request.render('dashboard_member12.registration_end')  
        cities = request.env['res.country.state'].sudo().search([('country_id', '=', 69)])
        ed_levels = request.env['res.edlevel'].sudo().search([])
        studies = request.env['field.study'].sudo().search([])
        ethnicity = request.env['ethnic.groups'].sudo().search([])
        subcities = request.env['membership.handlers.parent'].sudo().search([])
        weredas = request.env['membership.handlers.branch'].sudo().search([])
        return request.render("dashboard_member12.registration_form", {
                                                                    'ed_levels': ed_levels,
                                                                    'cities': cities,
                                                                    'subcities': subcities,
                                                                    'weredas': weredas,
                                                                    'ethnicity': ethnicity,
                                                                    'is_users': is_users,
                                                                    'studies': studies
                                                                })
