# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Times(models.Model):
    _name = "times"
    _description = "This model will create times"

    name = fields.Char(translate=True)
    time = fields.Float(required=True)

class Duration(models.Model):
    _name = "duration"
    _description = "This model will create duration time"

    name = fields.Char(translate=True)
    time = fields.Float(required=True)

class AppointmentSlot(models.Model):
    _name = 's2u.appointment.slot'
    _order = 'user_id, day, slot'
    _description = "Appointment Slot"
    
    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    user_id = fields.Many2one('hr.employee', string='User', required=True)
    day = fields.Selection(selection=_get_week_days, default='0', string="Day", required=True)
    slot = fields.Float('Slot', required=True)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if self.env.user.has_group('base.group_user'):
                record.x_css = '<style> .o_form_button_create {display:None}</style>'


    def make_more_slots(self):
        """This function will create more slots"""
        for record in self:
            wizard = self.env['make.more.slot'].create({
                'user_id': record.user_id.id,
                'day': record.day
            })
            return {
                'name': _('Create Slots Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'make.more.slot',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }


    @api.constrains('slot')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '12:00':
                raise ValidationError(_('The slot value must be between 0:00 and 12:00!'))
