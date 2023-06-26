# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Meeting(models.Model):
    _inherit = 'calendar.event'


    def change_attendee_status(self, status):
        res = super(Meeting, self).change_attendee_status(status)
        visit = self.env['fo.visit'].search([('event_id', '=', self.id)])
        if self.attendee_status == 'declined':
            if visit.state == 'draft':
                visit.state = 'cancel'
                for visitor in visit.visitor:
                    mail_temp = self.env.ref('s2u_online_appointment.appointment_denied_in')
                    mail_temp.send_mail(visit.id)
                self.active = False
        if self.attendee_status == 'accepted':
            if visit.state == 'draft':
                visit.state = 'approved'
                for visitor in visit.visitor:
                    mail_temp = self.env.ref('s2u_online_appointment.appointment_accepted_in')
                    mail_temp.send_mail(visit.id)
        return res
