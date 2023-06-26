# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class AppointmentOption(models.Model):
    _name = 's2u.appointment.option'
    _description = 'Appointment option'

    name = fields.Char(string='Appointment option', required=True, translate=True)
    duration = fields.Float('Duration of Appointment', required=True)
    user_specific = fields.Boolean(string='User specific', default=False)
    # users_allowed = fields.Many2many('hr.employee', 's2u_appointment_option_user_rel',
                                    #  'option_id', 'user_id', string='Users')
    users_allowed = fields.Many2many('hr.employee')
    # need_approval = fields.Selection([('needs approval', 'Needs Approval'), ('needs no approval', 'Does not Need Approval')], default="needs approval", required=True)
    # limit_of_appointment = fields.Integer()

    @api.constrains('duration')
    def _duration_validation(self):
        for option in self:
            if functions.float_to_time(option.duration) < '00:05' or functions.float_to_time(option.duration) > '08:00':
                raise ValidationError(_('The duration value must be between 0:05 and 8:00!'))

