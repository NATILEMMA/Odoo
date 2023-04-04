
import logging
from datetime import date
from datetime import timedelta,time, datetime
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os

from odoo.exceptions import UserError, Warning, ValidationError
import math
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from odoo import tools
import re
import base64
import requests
import babel
from dateutil.rrule import rrule, DAILY, WEEKLY
from pytz import timezone, UTC
import pytz
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from pytz import timezone
from pytz import utc

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
from odoo.tools.float_utils import float_round
import logging, pprint
_logger = logging.getLogger(__name__)



# This will generate 16th of days
ROUNDING_FACTOR = 16


CHECKTIME = [
    ('0', 'Check In'),
    ('1', 'Check Out'),
    ('2', 'Break Out'),
    ('3', 'Break In'),
    ('4', 'Overtime In'),
    ('5', 'Overtime Out')
]
STATES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
]


S_STATES = [
    ('draft', 'Draft'),
    ('requested', 'Requested'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class FIlteredHrAttendance(models.Model):
    _name = "hr.attendance.filtered"
    _description = "Filtered Attendance"
    _order = "check_in desc"

    def _default_employee(self):
        return self.env.user.employee_id
    date = fields.Date()
    month_y = fields.Char()
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False
    def string_to_datetime(value):
        """ Convert the given string value to a datetime in UTC. """
        return utc.localize(fields.Datetime.from_string(value))

   


    def filtering_action(self):
        _logger.info("################ Filtering Action###################")
        def string_to_datetime(value):
            """ Convert the given string value to a datetime in UTC. """
            return utc.localize(fields.Datetime.from_string(value))
        monthY = datetime.combine(fields.Date.from_string(datetime.now()), time.min)

        today = str(datetime.now()).split(' ')
        today = string_to_datetime(today[0])
        attendance = self.env['hr.attendance'].search([])
        _logger.info("Attendance:%s", attendance)

        attendance = self.env['hr.attendance'].search([('worked_hours','>',0)])
        _logger.info("Attendance:%s", attendance)
        for employee in attendance:
            _logger.info("Employee: %s", employee.employee_id.name)
            check_date = str(employee.check_in).split(' ')
            day = check_date[0].split('-')
            date = day[1]+"/"+day[2]+"/"+day[0]

            _logger.info("ddddddddddddddddddd %s",date)
            # converted_date = self.string_to_datetime(check_date[0])
            ttyme = datetime.combine(fields.Date.from_string(employee.check_in), time.min)
            locale = self.env.context.get('lang') or 'en_US'
            monthY = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))
            last_attendance_before_check_in = self.env['hr.attendance.filtered'].search([
                ('employee_id', '=', employee.employee_id.id),
                ('date', '=', check_date[0])
            ], order='check_in desc', limit=1)
            _logger.info('last_attendance_before_check_in : %s',last_attendance_before_check_in)
            check_in_time = self.env['check.time'].search([('name','=','check_in'),('state','=','active')], limit=1)
            check_out_time = self.env['check.time'].search([('name','=','check_out'),('state','=','active')], limit=1)
            
            if len(last_attendance_before_check_in) > 0:
                if last_attendance_before_check_in.check_in >= employee.check_in:
                    last_attendance_before_check_in.write({'check_in': employee.check_in})
                if last_attendance_before_check_in.check_out <= employee.check_out:
                    last_attendance_before_check_in.write({'check_out': employee.check_out})
            else:
                create = last_attendance_before_check_in.sudo().create({
                    'date': check_date[0],
                    'month_y': monthY,
                    'employee_id': employee.employee_id.id,
                    'department_id': employee.department_id.id,
                    'check_in': employee.check_in,
                    'check_out': employee.check_out,
                })
                
                _logger.info("############# createed %s",create)


        _logger.info("+++++++++++++++++++loooooooping closed++++++++++++++++++++")
        ttyme = datetime.combine(fields.Date.from_string(datetime.now()), time.min)
        _logger.info(ttyme)
        locale = self.env.context.get('lang') or 'en_US'
        month_y = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))

        
        filter = self.env['hr.attendance.filtered'].read_group([], fields=['month_y'], groupby=['month_y'])
        _logger.info("FILTER %s", filter)
        for val in filter:
            pass
        emp = self.env['hr.attendance.filtered'].read_group([], fields=['employee_id'], groupby=['employee_id'])
        _logger.info("Employee %s and %s", len(emp), emp)
        vv = 0
        for v in emp:
            # _logger.info("vvvvvvvvvvvvvvv %s",len(v))
            _logger.info("vvvvvvvvvvvvvvv %s",v)
            # _logger.info("vvvvvvvvvvvvvvv %s",v['__domain'][0])
            # _logger.info("vvvvvvvvvvvvvvv %s",v['__domain'][0][0])
            # _logger.info("vvvvvvvvvvvvvvv %s",v['__domain'][2])



            values = self.env['hr.attendance.filtered'].search([(v['__domain'][0]),('month_y','=',month_y)])
            _logger.info("----------------- %s",len(values))
            for vals in values:
                today = str(datetime.now()).split(' ')
                check = str(vals.check_in ).split(' ')
                _logger.info( "YYYYYYYYY %s, %s", check[0], today[0])
                if check[0] == today[0]:
                    _logger.info("%%%%%%%%%%%%%%%%")
                else:
                    _logger.info("----------------- %s",vals.worked_hours)
                    vv = vv + vals.worked_hours
                _logger.info("++++++++++ %s",vv)
                vv = 0




        
            


class AttendanceShiftControl(models.Model):
    _name = "attendance.shift.control"
    _description = "Attendance Shift Control"

    name = fields.Char()
    shift_type = fields.Many2one('shift.type')
    time_from = fields.Float(string='Time Form', compute="_compute_time")
    time_to = fields.Float(string='Time To', compute="_compute_time")

class ShiftType(models.Model):
    _name = "shift.type"
    _description = "Shift Type"

    name = fields.Char('Shift Name')

class AttendanceCheckTimeControl(models.Model):
    _name = "check.time"
    _description = "Attendance Check Time"

    name = fields.Char()
    time_from = fields.Char(string='Time From')
    time_to = fields.Char(string='Time TO')
    time_f = fields.Char(string='Time From')
    time_t = fields.Char(string='Time TO')
    punching_type = fields.Selection(CHECKTIME, string='Punching Type')
    state = fields.Selection(STATES,
                              'Status',
                              copy=False, default='draft',tracking=True)


    def action_actve(self):
        super(AttendanceCheckTimeControl, self).write({'state':'active'})

    @api.model
    def create(self,vals):
        _logger.info("vals:%s",vals)
        time_f = self.float_to_time(vals['time_from'])
        time_t = self.float_to_time(vals['time_to'])
        vals['time_f'] = str(time_f).split('(')[0]
        vals['time_t'] = str(time_t).split('(')[0]
        return super(AttendanceCheckTimeControl,  self).create(vals)

  
    def write(self,vals):
        _logger.info("vals:%s",vals)
        try:
            time_f = self.float_to_time(vals['time_from'])
            vals['time_f'] = str(time_f).split('(')[0]
        except:
            pass
        try:
            time_t = self.float_to_time(vals['time_to'])
            vals['time_t'] = str(time_t).split('(')[0]
        except:
            pass
        
        
        return super(AttendanceCheckTimeControl,  self).write(vals)




    def float_to_time(self,hours):
        """ Convert a number of hours into a time object. """
        _logger.info("############## float_to_time #############:%s",hours)
        if hours == 24.0:
            return time.max
        fractional, integral = math.modf(hours)
        return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    parent_name = fields.Many2one('hr.payroll.structure' ,string="Parent",index=True, store=True)
    # rule_ids = fields.One2many('hr.salary.rule', 'struct_id', string='Salary Rules', default={})
    
    
    @api.onchange('parent_name')
    def _compute_structure_parent(self):
        _logger.info(datetime.now())
        _logger.info(self.name)
        _logger.info(self.rule_ids)
        str_type = self.env['hr.payroll.structure'].sudo().search([('id','=', self.parent_name.id)])
        rules = []
        _logger.info("****************payroll**********")
        _logger.info(str_type.name)
        
        for l in range(len(str_type)):
            for line in str_type.rule_ids:
                _logger.info("oooooooooooooooooooooooooooooooooo")
                
                val = {}
                val['name']= line.name
                val['code']= line.code
                val['category_id'] =  line.category_id.id
                val['register_id'] = line.register_id.id
               
                rules.append((0,0, val))
        self['rule_ids'] = [ ]
        # self.env.cr.commit()
        self['rule_ids'] = rules
        self['parent_id'] = self.parent_name.id
        _logger.info(self['rule_ids'])


class PayrollContract(models.Model):
    _inherit = 'hr.contract'
    
    stucture_type_selector = fields.Many2one('hr.payroll.structure' ,string="Salary Structure Type",index=True, store=True)
    attendence_hours = fields.Float()
    absentee_hours = fields.Float()
    date = fields.Date()
    month = fields.Char()


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    paid_days = fields.Float(string='Paid Days', help="paid worked")

class SpecailReasonCategory(models.Model):
    _name = 'specail.reason.categories'

    name = fields.Char(string='Category') 


class SpecailCaseAbsent(models.Model):
    _name = 'specail.case.absent'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    
    employee_id = fields.Many2one('hr.employee', string='Employee',tracking=True,  default=lambda self: self.env.user.employee_id)
    reason_cat = fields.Many2one('specail.reason.categories', string='Reason Category')
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To",required=True)
    reason = fields.Text(tracking=True)
    month_y = fields.Char()
    state = fields.Selection(S_STATES,
                              'Status',
                              copy=False, default='draft',tracking=True)
    
    duration = fields.Char('Duration', tracking=True ,store=True)
    

    # @api.model
    # def create(self, vals):
    #     ttyme = datetime.combine(fields.Date.from_string(datetime.now()), time.min)
    #     locale = self.env.context.get('lang') or 'en_US'
    #     monthY = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))
    #     vals['month_y'] = monthY
    #     super(SpecailCaseAbsent, self).create(vals)

    @api.onchange('date_from','date_to')
    def _compute_date(self):
        duration = []
        
        if self.date_from and self.date_to:
            dur = self.date_to - self.date_from
            duration = str(dur).split(',')[0]
            self.duration = duration
           

    def action_request(self):
        ttyme = datetime.combine(fields.Date.from_string(datetime.now()), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        monthY = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))
        return super(SpecailCaseAbsent, self).write({'state':'requested', 'month_y': monthY})

    def action_approve(self):
        return super(SpecailCaseAbsent, self).write({'state':'approved'})

    def action_reject(self):
        return super(SpecailCaseAbsent, self).write({'state':'reject'})

    @api.model
    def create(self,vals):
        _logger.info("vals:%s",vals)
        date_to = str(vals['date_to']).split('-')[2]
        date_from = str(vals['date_from']).split('-')[2]

        dur = int(date_to) - int(date_from)

        duration = str(dur)+" "+"days"
        vals['duration'] = duration
        return super(SpecailCaseAbsent, self).create(vals)
        

    
    def write(self,vals):
        _logger.info("vals:%s",vals)
        case = self.env['specail.case.absent'].search([('id','in',self.ids)])
        _logger.info(case)
        _logger.info(case.date_from)
        _logger.info(case.date_to)
        _logger.info(int(str(case.date_from).split('-')[2]))

        # try:
        date_f = []
        date_t = []
        try:
            
            date_from = str(vals['date_from']).split('-')[2]
            date_f.append(date_from)
        except:
            date_f.append(int(str(case.date_from).split('-')[2]))


        try:
            
            date_to = str(vals['date_to']).split('-')[2]
            date_t.append(date_to)
        except:
            date_t.append(int(str(case.date_to).split('-')[2]))


        _logger.info(date_t)
        _logger.info(date_f)

        dur = int(date_t[0]) - int(date_f[0])

        duration = str(dur)+" "+"days"
        vals['duration'] = duration
        # except:
        #     pass
        return super(SpecailCaseAbsent, self).write(vals)
        


