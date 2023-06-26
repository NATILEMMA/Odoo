"""This file will deal with the archiving members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
import base64
import pytz
from odoo.addons.s2u_online_appointment.helpers import functions
all_days = {
            '0': 'Monday',
            '1': 'Tuesday',
            '2': 'Wednesday',
            '3': 'Thursday',
            '4': 'Friday',
            '5': 'Saturday',
            '6': 'Sunday'
            }

class VisitorIDWidget(models.TransientModel):
    _name = "visitor.id.widget"
    _description = "This will create widgets for the visitors"

    visit = fields.Many2one('fo.visit')
    visitor_id = fields.Many2one('fo.visitor', string="Visitor")
    visitor_id_number = fields.Many2one('visitor.number', string="Visitor ID", domain="[('occupied', '=', False)]")


    def action_done(self):
        """This function will add ID to each visitor"""
        wizard = self.env['visitor.id.widget'].search([('id', '=', self.id)])
        if self.visitor_id and self.visitor_id_number:
            self.visitor_id.visitor_id_number = self.visitor_id_number
            self.visitor_id_number.occupied = True
            for visitor in wizard.visit.visitor:
                if not visitor.visitor_id_number:
                    wizard = self.env['visitor.id.widget'].create({
                        'visit': wizard.visit.id,
                        'visitor_id': visitor.id
                    })
                    return {
                        'name': _('Add Visitor ID'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'visitor.id.widget',
                        'view_mode': 'form',
                        'res_id': wizard.id,
                        'target': 'new'
                    }
            wizard.visit.state = 'check_in'
        else:
            raise UserError(_("Please Fill In All The Given Fields"))
        


class RescheduleVisits(models.TransientModel):
    _name = "reschedule.visit"
    _description="This model will handle the archiving members"

    date = fields.Date(string="Date")
    check_in_float = fields.Float(string="Check In Time")
    duration_in_float = fields.Float(string="Estimated Duration of Meeting")
    check_out_float = fields.Float(string="Check Out Time", readonly=True, store=True)
    visits_id = fields.Many2one('fo.visit')


    def ld_to_utc(self, ld):

        date_parsed = datetime.strptime(ld, "%Y-%m-%d  %H:%M")
        ethTZ = pytz.timezone("Africa/Addis_Ababa")
        local = ethTZ
        local_dt = local.localize(date_parsed, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['reschedule.visit'].search([('id', '=', self.id)])
        if self.date and self.check_in_float and self.duration_in_float:
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
                    'check_in_float': wizard.visits_id.check_in_float,
                    'check_out_float': wizard.visits_id.check_out_float,
                    'duration_in_float': wizard.visits_id.duration_in_float,
                    'visits_id': wizard.visits_id.id
                })

                ethTZ = pytz.timezone("Africa/Addis_Ababa")
                date_app = self.date.strftime("%Y-%m-%d")
                start = date_app + " " + functions.float_to_time(self.check_in_float)
                date_start = self.ld_to_utc(start)

                wizard.visits_id.write({
                    'state': 'approved',
                    'date': self.date,
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
                mail_temp = self.env.ref('s2u_online_appointment.appointment_rescheduled_in')
                mail_temp.send_mail(wizard.visits_id.id)

        else:
            raise UserError(_("Please Fill In The Required Fields"))