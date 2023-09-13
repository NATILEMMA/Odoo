# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AppointmentOption(models.Model):
    _name = 's2u.appointment.option'
    _description = 'Appointment option'

    name = fields.Char(string='Appointment option', required=True, translate=True, size=64)
    duration = fields.Float('Duration of Appointment', required=True)
    user_specific = fields.Boolean(string='User specific', default=False)
    users_allowed = fields.Many2many('hr.employee')


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Appointment Option"))

    @api.constrains('duration')
    def _duration_validation(self):
        for option in self:
            if functions.float_to_time(option.duration) < '00:05' or functions.float_to_time(option.duration) > '08:00':
                raise ValidationError(_('The duration value must be between 0:05 and 8:00!'))

