# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
##############################################################################


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pytz
all_days = {
            '0': 'Monday',
            '1': 'Tuesday',
            '2': 'Wednesday',
            '3': 'Thursday',
            '4': 'Friday',
            '5': 'Saturday',
            '6': 'Sunday'
            }



class EmployeeEntry(models.Model):
    _name = 'fo.property.counter'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'employee'
    _description = 'Property Details'


    employee = fields.Many2one('hr.employee',  string="Employee", required=True)
    date = fields.Date(string="Date")
    check_in_time = fields.Char(string="Check In Time")
    check_out_time = fields.Char(string="Check Out Time")
    check_in_time_admin = fields.Float(string="Check In Time")
    check_out_time_admin = fields.Float(string="Check Out Time")
    visitor_belongings = fields.One2many('fo.belongings', 'belongings_id_fov_employee', string="Personal Belongings", copy=False)
    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Hours")
    state = fields.Selection([('draft', 'Draft'), ('prop_in', 'Check In'), ('prop_out', 'Check Out'), ('revise', 'Revise'), ('cancel', 'Cancelled'),],
        track_visibility='onchange', default='draft',
        help='If the employee taken the belongings to the company change state to ""Taken In""'
             'when he/she leave office change the state to ""Taken out""')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)


    def action_cancel(self):
        """This function will cancel management"""
        for record in self:
            record.state = "cancel"

    def unlink(self):
        """This function will delete visits in draft state only"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You Can Only Delete Entries that are in Draft State"))
        return super(EmployeeEntry, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'cancelled' or record.state == 'prop_out'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    @api.onchange('resource_calendar_id')
    def _change_resource_calendar_id(self):
        """This function will check the chnage in resource_calendar_id"""
        for record in self:
            if record.resource_calendar_id and record.date:
                days = record.resource_calendar_id.attendance_ids.mapped('dayofweek')
                new_list = []
                for day in days:
                    new_list.append(all_days[day])
                if record.date.strftime("%A") not in new_list:
                    record.date = False
                    raise UserError(_("The Date You Picked Isn't Apart of Your Working Days"))
                leaves = record.resource_calendar_id.global_leave_ids
                for leave in leaves:
                    if leave.date_from.date() <= record.date <= leave.date_to.date():
                        record.date = False
                        raise UserError(_("The Date You Picked Is A Holiday"))

    @api.onchange('date')
    def _check_holiday_weekend(self):
        """This function will check if picked date is a holiday or weekend"""
        for record in self:
            if not record.date:
                raise UserError(_("Please Add A Date First"))
            if not record.resource_calendar_id and record.date:
                record.date = False
                raise UserError(_("Please Add Working Days First"))
            if record.date and record.resource_calendar_id:
                if record.date < date.today():
                    raise UserError(_("Please Add A Date After Today"))
                days = record.resource_calendar_id.attendance_ids.mapped('dayofweek')
                new_list = []
                for day in days:
                    new_list.append(all_days[day])
                if record.date.strftime("%A") not in new_list:
                    record.date = False
                    raise UserError(_("The Date You Picked Isn't Apart of Your Working Days"))
                leaves = record.resource_calendar_id.global_leave_ids
                for leave in leaves:
                    if leave.date_from.date() <= record.date <= leave.date_to.date():
                        record.date = False
                        raise UserError(_("The Date You Picked Is A Holiday"))

    def action_prop_in(self):
        for record in self:
            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            timeEth = (datetime.now(ethTZ) - relativedelta(hours=6)).strftime("%H:%M")
            record.check_in_time = timeEth
            for visit in record.visitor_belongings:
                if not visit.property_count:
                    raise UserError(_('Please Add The Amount.'))
                visit.in_or_out = 'in'
            count = 0
            number = 0
            for data in record.visitor_belongings:
                if not data.property_count:
                    raise UserError(_('Please Add The Amount.'))
                if data.permission == '1':
                    count += 1
                number = data.number
            # if number == count:
            #     raise UserError(_('No property can be taken in.'))
            # else:
            record.state = 'prop_in'

    def action_prop_out(self):
        """This function will checkout management"""
        for record in self:
            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            timeEth = (datetime.now(ethTZ) - relativedelta(hours=6)).strftime("%H:%M")
            record.check_out_time = timeEth
            for item in record.visitor_belongings:
                if item.in_or_out == 'in' and item.check_out:
                    item.in_or_out = 'in_out'
                elif item.in_or_out == 'in' and item.check_out == False:
                    item.in_or_out = 'in'
                elif item.in_or_out == False and item.check_out == True:
                    item.in_or_out = 'out'
                elif item.in_or_out == False and item.check_out == False:
                    raise UserError(_("There is an item that is not checked out and hasn\'t been checked in."))
            record.state = "prop_out"


    def action_prop_in_admin(self):
        for record in self:
            for visit in record.visitor_belongings:
                visit.in_or_out = 'in'
            count = 0
            number = 0
            for data in record.visitor_belongings:
                if not data.property_count:
                    raise UserError(_('Please Add The Amount.'))
                if data.permission == '1':
                    count += 1
                number = data.number
            # if number == count:
            #     raise UserError(_('No property can be taken in.'))
            # else:
            record.state = 'prop_in'

    def action_prop_out_admin(self):
        """This function will checkout management"""
        for record in self:
            for item in record.visitor_belongings:
                if item.in_or_out == 'in' and item.check_out:
                    item.in_or_out = 'in_out'
                elif item.in_or_out == 'in' and item.check_out == False:
                    item.in_or_out = 'in'
                elif item.in_or_out == False and item.check_out == True:
                    item.in_or_out = 'out'
                elif item.in_or_out == False and item.check_out == False:
                    raise UserError(_("There is an item that is not checked out and hasn\'t been checked in."))
            record.state = "prop_out"


    def action_revise(self):
        """This function will revise the management"""
        for record in self:
            record.state = 'revise'





