# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Meeting(models.Model):
    _inherit = 'calendar.event'


    def change_attendee_status(self, status):
        res = super(Meeting, self).change_attendee_status(status)
        appointment = self.env['s2u.appointment.registration'].search([('event_id', '=', self.id)])
        visit = self.env['fo.visit'].search([('event_id', '=', self.id)])
        if self.attendee_status == 'declined':
            if appointment.state == 'pending' or appointment.state == 'valid':
                appointment.state = 'cancel'
            if visit.state == 'draft':
                visit.state = 'cancel'
                mail_temp = self.env.ref('visitor_gate_management.appointment_denied_in')
                mail_temp.send_mail(visit.id)
                visit.deactivate_activity(visit)
            self.active = False
        if self.attendee_status == 'accepted':
            if appointment.state == 'pending':
                appointment.state = 'valid'
            if visit.state == 'draft':
                visit.state = 'approved'
                mail_temp = self.env.ref('visitor_gate_management.appointment_accepted_in')
                mail_temp.send_mail(visit.id)
                visit.deactivate_activity(visit)
        return res
