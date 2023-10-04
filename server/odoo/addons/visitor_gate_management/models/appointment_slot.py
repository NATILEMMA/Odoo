# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import random

class Times(models.Model):
    _name = "times"
    _description = "This model will create times"


    name = fields.Char()
    time = fields.Float(required=True)

class Duration(models.Model):
    _name = "duration"
    _description = "This model will create duration time"


    name = fields.Char()
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


    def _default_employee(self):
        """This function will find the default employee"""
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id


    name = fields.Char(string="name", required=True, readonly=True, default="Name")
    user_id = fields.Many2one('hr.employee', string='User', required=True, domain="[('user_id', '!=', False)]", default=_default_employee, readonly=True)
    day = fields.Selection(selection=_get_week_days, default='0', string="Day", required=True)
    slot_start = fields.Float('Start Time', required=True)
    slot = fields.Float('Slot')
    slot_end = fields.Float('End Time', required=True)
    # x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    # adjusted_by = fields.Selection(selection=[('employee', 'Employees'), ('manager', 'Managers')], default='employee', required=True)
    # state = fields.Selection(selection=[('draft', 'Draft'), ('waiting for approval', 'Waiting For Approval'), ('approved', 'Approved')], default='draft', required=True, track_visibility='onchange')
    # options = fields.Many2one('s2u.appointment.option', required=True)


    _sql_constraints = [
                        ('check_time', 'CHECK (slot_end > slot_start)', 'End Time Must Be Greater Than Start Time')
                    ]

    @api.model
    def create(self, vals):
        """This function will change fields upon creation"""
        res = super(AppointmentSlot, self).create(vals)
        res.name = res.user_id.name + res.day + str(random.randint(1,100))
        if res.slot_start == 0.00 or res.slot_end == 0.00:
            raise UserError(_("Slot Time Can't Be 0"))
        return res

    @api.onchange('slot_start', 'slot_end')
    def _slot_start_on_change(self):
        """This function will check the start time"""
        for record in self:
            if record.slot_start and record.slot_end:
                if record.slot_start == 0.00:
                    raise UserError(_("Slot Start Time Can't Be 0"))
                if record.slot_end == 0.00:
                    raise UserError(_("Slot End Time Can't Be 0"))

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.adjusted_by == 'manager' and not self.env.user.has_group('visitor_gate_management.group_managers'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    # def set_to_draft(self):
    #     """This function will set the slot into draft state"""
    #     for record in self:
    #         record.state = 'draft'

    # def approve_slots(self):
    #     """This function will approve Slots"""
    #     for record in self:
    #         record.state = 'approved'


    # def send_slots_for_approval(self):
    #     """This function will approve Slots"""
    #     for record in self:
    #         record.state = 'waiting for approval'

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


    @api.constrains('slot_start')
    def _slot_start_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot_start) < '00:00' or functions.float_to_time(slot.slot_start) > '12:00':
                raise ValidationError(_('The Start Time value must be between 0:00 and 12:00!'))


    @api.constrains('slot_end')
    def _slot_end_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot_end) < '00:00' or functions.float_to_time(slot.slot_end) > '12:00':
                raise ValidationError(_('The End Time value must be between 0:00 and 12:00!'))
