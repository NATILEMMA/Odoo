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
    users_allowed = fields.Many2many('hr.employee', domain="[('user_id', '!=', False)]")
    adjusted_for = fields.Selection(selection=[('organization', 'Organization'), ('private', 'Private')], default='organization', required=True, string="Slot Created For")
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    state = fields.Selection(selection=[('draft', 'Draft'), ('waiting for approval', 'Waiting For Approval'), ('approved', 'Approved')], default='draft', required=True, track_visibility='onchange')


    def unlink(self):
        """This function will delete option"""
        for record in self:
            if record.state != 'draft':
                raise UserError((_("You Can Only Delete Options in Draft State")))
        return super(AppointmentOption, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state != 'draft':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def send_for_approval(self):
        """This function will send options for approval"""
        for record in self:
            record.state = 'waiting for approval'
 
    def approve_options(self):
        """This function will approve options"""
        for record in self:
            record.state = 'approved'

    def set_to_draft(self):
        """This function will set to new"""
        for record in self:
            record.state = 'draft'


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

