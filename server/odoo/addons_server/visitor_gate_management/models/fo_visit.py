# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
##############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.addons.s2u_online_appointment.helpers import functions
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
_logger = logging.getLogger(__name__)

class RescheduledTime(models.Model):
    _name = "rescheduled.time"
    _description = "This model will reschedule a visit"

    date = fields.Date(string="Date")
    check_in_float = fields.Float(string="Check In Time")
    duration_in_float = fields.Float(string="Estimated Duration of Meeting")
    check_out_float = fields.Float(string="Check Out Time")
    visits_id = fields.Many2one('fo.visit')
    

class Properties(models.Model):
    _name = "properties"
    _description = "This model will create belongings"

    name = fields.Char(translate=True, required=True, size=64)

    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each Property should be Unique')
                        ]

    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Property Name"))

class LockerName(models.Model):
    _name = "locker.name"
    _description = "This model will create a locker name"

    name = fields.Char(required=True, size=64,translate=True)

    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each Locker Name should be Unique')
                        ]


class VisitDetails(models.Model):
    _name = 'fo.visit'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Visit record handler'


    def _default_creator(self):
        """This function will create the default creator"""
        return self.env['res.users'].search([('id', '=', self.env.user.id)], limit=1).id


    def _default_standard(self):
        """This will create the default standard date"""
        return self.env['resource.calendar'].search([('name', '=', 'Standard 40 hours/week')], limit=1).id

    name = fields.Char(string="sequence", default=lambda self: _('New'),translate=True)
    all_visitor = fields.Char(string='Employees', compute='_get_visitor', store=True,translate=True)
    visitor = fields.Many2many("res.partner", domain="[('is_company', '=', False)]", string='Visitors', required=True, store=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    reason = fields.Many2one('fo.purpose', string='Purpose Of Visit', required=True,
                              help='Enter the reason for visit', translate=True)
    visitor_belongings = fields.One2many('fo.belongings', 'belongings_id_fov_visitor', string="Personal Belongings",
                                         help='Add the belongings details here.')
    rescheduled_visits_ids = fields.One2many('rescheduled.time', 'visits_id')
    date = fields.Date(string="Date")
    check_in_time = fields.Char(string="Check In Time",translate=True)
    check_in_float = fields.Float(string="Check In Time")
    duration_in_float = fields.Float(string="Estimated Duration of Meeting")
    check_out_time = fields.Char(string="Check Out Time")
    start_time = fields.Char(string="Visit Start Time")
    check_out_float = fields.Float(string="Check Out Time", compute="_check_out_time", store=True)
    visit_with = fields.Selection([('employee', 'Employee'), ('department', 'Department')], default="employee")
    department = fields.Many2one('hr.department',  string="Department")
    visiting_employee = fields.Many2many('hr.employee', string="Meeting With", store=True, domain="[('user_id', '!=', False)]")
    employee = fields.Char(string='Employees', compute='_get_employees', store=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, required=True)
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('check_in', 'Checked In'), ('check_out', 'Checked Out'), ('revise', 'Revised'), ('cancel', 'Cancelled'),], track_visibility='onchange', default='draft')
    no_visiters = fields.Boolean(default=False)
    disappear_approve = fields.Boolean(default=False)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Hours", default=_default_standard)
    event_id = fields.Many2one('calendar.event')
    meeting_minute = fields.Text('Meeting Minute',translate=True)
    rescheduled = fields.Boolean(default=False)
    done = fields.Boolean(default=False)
    started = fields.Boolean(default=False)
    creator = fields.Many2one('res.users', default=_default_creator, readonly=True)
    from_portal = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        if vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('fo.visit') or _('New')
            visitor = vals['visitor']
            if len(visitor[0][2]) == 1:
                vals['no_visiters'] = True
                if not vals['phone'] or not vals['email']:
                    visit = self.env['res.partner'].search([('id', '=', visitor[0][2])])
                    vals['phone'] = visit.phone
                    vals['email'] = visit.email
            if len(visitor[0][2]) > 1:
                vals['no_visiters'] = False

        res =  super(VisitDetails, self).create(vals)
        if res.check_in_float == 0.00 or res.duration_in_float == 0.00:
            raise UserError(_("Please Add Check In Time and Duration of Visit"))
        # if not res.date:
        #     raise UserError(_("Please Add the Date of Visit"))
        if (res.creator.has_group('visitor_gate_management.group_employees')):
            users = []
            for visitor in res.visitor:
                user = self.env['res.users'].search([('partner_id', '=', visitor.id)]).id
                users.append(user)
            if (res.creator.id in res.visiting_employee.user_id.ids):
                res.state = 'approved'
            if (res.creator.id in users):
                res.state = 'draft'
            if (res.creator.id not in users) and (res.creator.id not in res.visiting_employee.user_id.ids):
                raise UserError(_("You Can't Create Visits for Other Employees"))
        return res
        

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state == 'revise' or record.state == 'check_out' or record.state == 'cancel' or \
               (self.env.user.has_group('visitor_gate_management.group_employees') and (record.state == 'draft' or record.state == 'approved' or record.state == 'check_out' or record.state == 'revise' or record.state == 'cancel')):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            if record.state == 'draft' and record.creator.id != self.env.user.id:
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def unlink(self):
        """This function will delete visits in draft state only"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You Can Only Delete Visits in Draft State"))
        return super(VisitDetails, self).unlink()

    def deactivate_activity(self, record):
        """This function will deactivate an activity"""
        model = self.env['ir.model'].search([('model', '=', 'fo.visit'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Visitor Approval')], limit=1)
        activity = self.env['mail.activity'].search([('res_id', '=', record.id), ('res_model_id', '=', model.id), ('activity_type_id', '=', activity_type.id)])
        activity.unlink()


    @api.depends('visiting_employee')
    def _get_employees(self):
        """This function will find the employeees in visit"""
        for record in self:
            tag_custom = ''
            if record.visiting_employee:
                tag_custom = ','.join([p.name for p in record.visiting_employee])
            else:
                tag_id_custom = ''
            record.employee = tag_custom

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                for st in record.phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))


    @api.depends('visitor')
    def _get_visitor(self):
        """This function will find the employeees in visit"""
        for record in self:
            tag_custom = ''
            if record.visitor:
                tag_custom = ','.join([p.name for p in record.visitor])
            else:
                tag_id_custom = ''
            record.all_visitor = tag_custom

    @api.onchange('visit_with')
    def _make_false(self):
        """This function will erase fields"""
        for record in self:
            if record.visit_with:
                if record.visit_with == 'department':
                    record.disappear_approve = True
                    record.visiting_employee = False
                    record.department = False
                if record.visit_with == 'employee':
                    record.disappear_approve = True
                    record.visiting_employee = False
                    record.department = False
            else:
                record.disappear_approve = False
                record.visiting_employee = False
                record.department = False

    @api.onchange('department')
    def _make_employee_false(self):
        """This function will erase fields"""
        for record in self:
            if record.department:
                record.visiting_employee = False
                record.visiting_employee = record.department.secretary_ids.ids


    @api.depends('check_in_float', 'duration_in_float')
    def _check_out_time(self):
        """This function will compute check out time"""
        for record in self:
            if record.check_in_float and record.duration_in_float:
                out = record.duration_in_float + record.check_in_float
                record.check_out_float = out
                if record.check_out_float > 11.0:
                    raise UserError(_("Sorry, This Time is Out Of The Range of Regular Working Hours"))
                if record.check_in_float == 0.00 or record.duration_in_float == 0.00:
                        raise UserError(_("Please Add Check In Time and Duration of Visit"))
                if record.check_in_float < 0.00 or record.duration_in_float < 0.00:
                        raise UserError(_("Check In Time and Duration of Visit Can't Be Negative"))
                # record.check_in_float = function.time_to_float(record.check_in_float)
                # record.duration_in_float = function.time_to_float(record.duration_in_float)


    def ld_to_utc(self, ld):

        date_parsed = datetime.strptime(ld, "%Y-%m-%d  %H:%M")
        ethTZ = pytz.timezone("Africa/Addis_Ababa")
        local = ethTZ
        local_dt = local.localize(date_parsed, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    @api.onchange('date')
    def _check_holiday_weekend(self):
        """This function will check if picked date is a holiday or weekend"""
        for record in self:
            if not record.resource_calendar_id and record.date:
                record.date = False
                raise UserError(_("Please Add Working Days First"))
            if record.date:
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

    def action_send_to_approve(self):
        """This function will sned it to the respective personnel for approval"""
        for record in self:
            all_name = ""
            for name in record.visitor:
                all_name += name.name + ", "
                new = "With " + all_name[:-2]

            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            date_app = record.date.strftime("%Y-%m-%d")
            start = date_app + " " + functions.float_to_time(record.check_in_float)
            date_start = self.ld_to_utc(start)

            all_employee = []
            appointee_ids = self.env['hr.employee'].sudo().search([('id', 'in', record.visiting_employee.ids)])
            for appointee in appointee_ids:
                partner = self.env['res.partner'].sudo().search([('id', '=', appointee.user_partner_id.id)])
                if partner:
                    all_employee.append(partner.id)
            all_attendee = all_employee
            appointment = self.env['calendar.event'].sudo().with_context(detaching=True).create({
                'name': "Visits",
                'description': new,
                'start': date_start.strftime("%Y-%m-%d %H:%M"),
                'stop': (date_start + timedelta(minutes=round(record.duration_in_float * 60))).strftime("%Y-%m-%d %H:%M"),
                'duration': record.duration_in_float,
                'partner_ids': [(6, 0, all_attendee)]
            })
            appointment.attendee_ids.write({
                'state': 'tentative'
            })
            record.event_id = appointment
            for employee in record.visiting_employee:
                message = _("You Have Visitors Who Have An Appointment on %s at %s") % (str(record.date), functions.float_to_time(record.check_in_float))
                title = _("<h4>Visit Approval</h4>")
                model = self.env['ir.model'].search([('model', '=', 'fo.visit'), ('is_mail_activity', '=', True)])
                activity_type = self.env['mail.activity.type'].search([('name', '=', 'Visitor Approval')], limit=1)
                if employee.user_id:
                    activity = self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Visitor Approval",
                        'date_deadline': date.today() + relativedelta(minutes=30),
                        'user_id': employee.user_id.id,
                        'res_model_id': model.id,
                        'res_id': record.id,
                        'activity_type_id': activity_type.id
                    })
                    employee.user_id.notify_warning(message, title, True)
            message = _("Approval Has Been Sent Successfully")
            title = _("<h4>Approval Sent</h4>")
            self.env.user.notify_success(message, title, True)


    def action_cancel(self):
        """This function will cancel a visit"""
        for record in self:
            record.event_id.attendee_ids.write({
                'state': 'declined'
            })
            registration = self.env['s2u.appointment.registration'].search([('event_id', '=', record.event_id.id)])
            if registration:
                registration.state = 'cancel'
            mail_temp = self.env.ref('visitor_gate_management.appointment_denied_in')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)
            record.state = "cancel"

    def action_approve(self):
        """This function will approve a visit"""
        for record in self:
            record.state = "approved"

    def action_start(self):
        """This function will start meeting"""
        for record in self:
            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            timeEth = (datetime.now(ethTZ) - relativedelta(hours=6)).strftime("%H:%M")
            record.start_time = timeEth
            record.started = True

    def action_approve_employee(self):
        """This function will approve from employee"""
        for record in self:
            record.state = "approved"
            record.event_id.attendee_ids.write({
                'state': 'accepted'
            })
            registration = self.env['s2u.appointment.registration'].search([('event_id', '=', record.event_id.id)])
            if registration:
                registration.state = 'valid'
            mail_temp = self.env.ref('visitor_gate_management.appointment_accepted_in')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)

    def action_reschedule(self):
        """This function will approve a visit"""
        for record in self:
            wizard = self.env['reschedule.visit'].create({
                'visits_id': record.id
            })
            return {
                'name': _('Reschedule Visits'),
                'type': 'ir.actions.act_window',
                'res_model': 'reschedule.visit',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }           

    def action_after_check_in_reschedule(self):
        """This function will reschedule for long visits"""
        for record in self:
            wizard = self.env['reschedule.visit'].create({
                'visits_id': record.id
            })
            return {
                'name': _('Reschedule Visits'),
                'type': 'ir.actions.act_window',
                'res_model': 'reschedule.visit',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }          

    def action_revise(self):
        """This function will revise the management"""
        for record in self:
            record.state = 'revise'

    def action_check_in(self):
        for record in self:
            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            timeEth = (datetime.now(ethTZ) - relativedelta(hours=6)).strftime("%H:%M")
            record.check_in_time = timeEth

            count = 0
            number = 0
            for data in record.visitor_belongings:
                data.in_or_out = 'in'
                if not data.property_count:
                    raise UserError(_('Please Add The Amount.'))
                if data.permission == '1':
                    count += 1
                number = data.number
            for visitor in record.visitor:
                if not visitor.visitor_id_number:
                    wizard = self.env['visitor.id.widget'].create({
                        'visit': record.id,
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

    def action_check_out(self):
        for record in self:
            if record.meeting_minute == '<p><br></p>' and record.started == True:
                raise UserError(_("Please Add Meeting Minute For This Visit"))
            ethTZ = pytz.timezone("Africa/Addis_Ababa")
            timeEth = (datetime.now(ethTZ) - relativedelta(hours=6)).strftime("%H:%M")
            record.check_out_time = timeEth
            if record.event_id:
                appointment = self.env['s2u.appointment.registration'].search([('event_id', '=', record.event_id.id)])
                try:
                    appointment.write({
                        'state': 'ended',
                        'meeting_minute': record.meeting_minute
                    })
                except:
                    pass
            for item in record.visitor_belongings:
                if item.in_or_out == 'in' and item.check_out:
                    item.in_or_out = 'in_out'
                elif item.in_or_out == 'in' and item.check_out == False:
                    item.in_or_out = 'in'
                elif item.in_or_out == False and item.check_out == True:
                    item.in_or_out = 'out'
                elif item.in_or_out == False and item.check_out == False:
                    raise UserError(_("There is an item that is not checked out and hasn\'t been checked in."))
            record.state = 'check_out'


    def accept_id(self):
        """This function will make sure ID are received from Visitors"""
        for record in self:
            for visitor in record.visitor:
                visitor.visitor_id_number.occupied = False
                visitor.visitor_id_number = False
            record.done = True


    def action_check_in_admin(self):
        for record in self:
            count = 0
            number = 0
            for data in record.visitor_belongings:
                data.in_or_out = 'in'
                if not data.property_count:
                    raise UserError(_('Please Add The Amount.'))
                if data.permission == '1':
                    count += 1
                number = data.number
            record.state = 'check_in'

    def action_check_out_admin(self):
        for record in self:
            if record.meeting_minute == '<p><br></p>':
                raise UserError(_("Please Add Meeting Minute For This Visit"))
            if record.event_id:
                appointment = self.env['s2u.appointment.registration'].search([('event_id', '=', record.event_id.id)])
                try:
                    appointment.write({
                        'state': 'ended',
                        'meeting_minute': record.meeting_minute
                    })
                except:
                    pass
            for item in record.visitor_belongings:
                if item.in_or_out == 'in' and item.check_out:
                    item.in_or_out = 'in_out'
                elif item.in_or_out == 'in' and item.check_out == False:
                    item.in_or_out = 'in'
                elif item.in_or_out == False and item.check_out == True:
                    item.in_or_out = 'out'
                elif item.in_or_out == False and item.check_out == False:
                    raise UserError(_("There is an item that is not checked out and hasn\'t been checked in."))
            record.state = "check_out"

class PersonalBelongings(models.Model):
    _name = 'fo.belongings'
    _description = "This model will handle Belongings of the Visitors"

    check_out = fields.Boolean(default=False, string="Check Out")
    property_name = fields.Many2one('properties', string="Property", help='Employee belongings name')
    property_description = fields.Text(string="Description", translate=True)
    property_count = fields.Integer(string="Amount", help='Amount of property')
    number = fields.Integer(compute='get_number', store=True, string="Sl")
    belongings_id_fov_visitor = fields.Many2one('fo.visit', string="Belongings")
    belongings_id_fov_employee = fields.Many2one('fo.property.counter', string="Belongings")
    permission = fields.Selection([('0', 'Allowed'), ('1', 'Not Allowed'), ('2', 'Allowed With Permission'),], 'Permission',
                 required=True, index=True, default='0', track_visibility='onchange')
    visitor_id = fields.Many2one("res.partner", string='Visitor')
    phone = fields.Char(string="Phone", related="visitor_id.phone", store=True,translate=True)
    reference_no = fields.Char(string="Reference Number", size=64,translate=True)
    locker_number = fields.Many2one("locker.name", string="Locker Number")
    in_or_out = fields.Selection([('in', 'In'), ('out', 'Out'), ('in_out', 'In/Out')], readonly=True)
    visitor_id_number = fields.Many2one('visitor.number', related="visitor_id.visitor_id_number", string="Visitor ID Number", readonly=True)


    @api.onchange('check_out')
    def _deny_check_out_before_check_in(self):
        """This will raise error if checkout before check in"""
        for record in self:
            if record.belongings_id_fov_employee.state == "draft" and record.check_out:
                record.check_out = False
                raise UserError(_("This check is only used when checking out"))

    @api.depends('belongings_id_fov_visitor', 'belongings_id_fov_employee')
    def get_number(self):
        for visit in self.mapped('belongings_id_fov_visitor'):
            number = 1
            for line in visit.visitor_belongings:
                line.number = number
                number += 1
        for visit in self.mapped('belongings_id_fov_employee'):
            number = 1
            for line in visit.visitor_belongings:
                line.number = number
                number += 1



class VisitPurpose(models.Model):
    _name = 'fo.purpose'
    _description = "This model will handle Purpose of Visits"

    name = fields.Char(string='Purpose', required=True, help='Meeting purpose in short term.eg:Meeting.', translate=True, size=64)
    description = fields.Text(string='Description Of Purpose', help='Description for the Purpose.',translate=True)


    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each Purpose should be Unique')
                        ]


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Purpose of Visit"))






