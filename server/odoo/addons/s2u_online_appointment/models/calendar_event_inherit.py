# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Meeting(models.Model):
    _inherit = 'calendar.event'


    def change_attendee_status(self, status):
        res = super(Meeting, self).change_attendee_status(status)
        if self.attendee_status == 'declined':
            appointment = self.env['s2u.appointment.registration'].search([('event_id', '=', self.id)])
            if appointment.state == 'pending' or appointment.state == 'valid':
                appointment.state = 'cancel'
                mail_temp = self.env.ref('s2u_online_appointment.appointment_denied')
                mail_temp.send_mail(self.id)
                self.active = False
        if self.attendee_status == 'accepted':
            appointment = self.env['s2u.appointment.registration'].search([('event_id', '=', self.id)])
            if appointment.state == 'pending':
                appointment.state = 'valid'
                mail_temp = self.env.ref('s2u_online_appointment.appointment_accepted')
                mail_temp.send_mail(self.id)
        return res
