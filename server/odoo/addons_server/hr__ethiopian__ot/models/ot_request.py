import math
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta,date


class HROvertimeRequest(models.Model):
    _name = 'hr_ethiopian_ot.request'
    _description = "HR Overtime"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    name = fields.Char('Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id,
                                  required=True)
    hr_payslip = fields.Many2one('hr.payslip', string='payslip')

    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  )
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True)
    state = fields.Selection([
                              ('Pre_draft', 'Draft'),
                              ('draft', 'Checked'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('calculated', 'Calculated'),
                              ('refused', 'Refused'),
                              ('paid', 'Paid')], string="State",
                             default="Pre_draft", tracking=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date to')
    ot_times = fields.One2many('hr_ethiopian_ot.times', 'request_id')
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   default=lambda self: self.env.uid,
                                   store=True)
    company_id = fields.Many2one('res.company', 'Company', index=True,
                                 default=lambda self: self.env.company)
    payslip_paid = fields.Boolean('Paid in Payslip', readonly=True)
    total = fields.Float('Total', digits=(12, 2))


    def make_overtimes(self, date_from, date_to, request_id, delta):
        """This function will create ot time dates"""
        while date_from <= date_to:
            ot_times = {
                'date_from': date_from,
                'date_name': date_from.strftime('%A'),
                'request_id': request_id.id
            }
            holiday = self.env['hr_ethiopian_ot.times'].create(ot_times)

            date_from += delta
        return


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def calculate(self):

        clause_final = [('id', '=', self.contract_id.id)]
        search_results = self.env['hr.contract'].search(clause_final).ids
        if search_results:
            for search_result in self.env['hr.contract'].browse(search_results):
                payment_per_hour = search_result.over_hour
            total = 0.0
            clause_final_times = [('request_id', '=', self.id)]
            search_results_times = self.env['hr_ethiopian_ot.times'].search(clause_final_times).ids
            if search_results_times:
                for search_results_time in self.env['hr_ethiopian_ot.times'].browse(search_results_times):
                    payment_total = payment_per_hour * search_results_time.rate_amount * search_results_time.worked_hour
                    total = total + payment_total
                    search_results_time.write({'payment_total':payment_total,'payment_per_hour':payment_per_hour})
                self.write({"total":total, "state":"calculated"})
        else:
            raise ValidationError('The selected employee has no contract')

    @api.model
    def create(self, values):
        request_id = super(HROvertimeRequest, self.sudo()).create(values)
        if request_id.date_from > request_id.date_to:
            raise ValidationError('Start Date must be less than End Date or the time must be less than 24')
        date_from = request_id.date_from
        date_to = request_id.date_to
        delta = timedelta(days=1)
        contract = self.env['hr.contract'].search([('id', '=', request_id.contract_id.id), ('state', '=', 'open')])
        if contract.can_work_on_shift:
            shifts = self.env['hr.employee.shift'].search([('employee_id', '=', request_id.employee_id.id)])
            if date_from < shifts[0].start_date:
                message = "You Don't Have Any Shift Assigned To You Before " + str(shifts[0].start_date)
                raise ValidationError(_(message))
            else:
                if date_to <= date.today():
                    self.make_overtimes(date_from, date_to, request_id, delta)
                else:
                    date_to = date.today()
                    self.make_overtimes(date_from, date_to, request_id, delta)
        else:
            if date_to <= date.today():
                    self.make_overtimes(date_from, date_to, request_id, delta)
            else:
                date_to = date.today()
                self.make_overtimes(date_from, date_to, request_id, delta)
        return request_id


    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on same day!'))


    def cheak(self):
     if self.date_from and self.date_to:
         employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
         self.name = employee.name
         group = self.env.ref('account.group_account_invoice', False)
         return self.sudo().write({
            'state': 'draft'})


    def set_to_waiting(self):
        return self.sudo().write({
            'state': 'f_approve'})


    def submit_to_f(self):
        # notification to employee
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your OverTime Request Waiting Finance Approve .."
        msg = _(body)
        group = self.env.ref('account.group_account_invoice', False)
        recipient_partners = []
        body = "You Get New Time in Lieu Request From Employee : " + str(
            self.employee_id.name)
        msg = _(body)
        return self.sudo().write({
            'state': 'f_approve'
        })


    def approve(self):
     
        # notification to employee :
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your Time In Lieu Request Has been Approved ..."
        msg = _(body)
        tracking = "1"
        return self.sudo().write({
            'state': 'approved',

        })

    def return_to_draft(self):

       self.state = 'draft'

    def recheck(self):
       self.state = 'f_approve'

    def reject(self):
       self.state = 'refused'


class HROvertimes(models.Model):
    _name = 'hr_ethiopian_ot.times'
    _description = 'Overtime works based on Ethiopian rule'

    date_from = fields.Date('Date From', required=True)
    start_time = fields.Float(string='OT Start Time')
    end_time = fields.Float(string='OT End Time')
    user_start_time = fields.Float(string='Req StartTime', store=True)
    user_end_time = fields.Float(string='Req EndTime', store=True)
    request_id = fields.Many2one('hr_ethiopian_ot.request', string="request Id")
    ot_id = fields.Many2one('hr_ethiopian_ot.rate', string="Rate ")

    ot_type = fields.Char(string='OT Type')
    rate_amount = fields.Float(string='OT Rate')
    payment_per_hour = fields.Float(string='Payment/Hour')
    payment_total = fields.Float(string='Total')
    worked_hour = fields.Float(string="Worked Hour")
    payment = fields.Float(string="Calculated Payment")
    date_name = fields.Char(string='Date name')


    def correct_times(self, day_periods, record):
        """This function will take attendance days and check if OT time mates the working time"""
        # None Work Days
        days = day_periods.mapped('name')
        new_days = [day.split()[0] for day in days]
        if record.date_name not in new_days:
            record.user_start_time = record.start_time
            record.user_end_time = record.end_time
            record.worked_hour = record.end_time - record.start_time
            search_results = self.env['hr_ethiopian_ot.rate'].search([('type', '=', 'weekend')])
            if search_results:
                record.ot_id = search_results.id
                record.ot_type = search_results.type
                record.rate_amount = search_results.rate
        # Work Days
        else:
            record.user_start_time = record.start_time
            record.user_end_time = record.end_time 
            check_shifts = True
            for day in day_periods:
                if day_periods[0].hour_to == day.hour_to:
                    continue
                else:
                    check_shifts = False
            if check_shifts: 
                print("Of Shift")
                end_time = day_periods[0].hour_to
                print(day_periods.mapped('hour_to'))
                print(end_time)
                if record.start_time <= record.end_time <= end_time:
                    message = f"From {day_periods[0].hour_from} to {day_periods[0].hour_to} is your regular working hour."
                    record.start_time = 0.00
                    record.end_time = 0.00
                    record.user_start_time = 0.00
                    record.user_end_time = 0.00
                    raise ValidationError(_(message))
                elif record.start_time <= end_time < record.end_time:
                    record.start_time = end_time
                    record.worked_hour = record.end_time - record.start_time
                elif end_time < record.start_time < record.end_time:
                    record.start_time = end_time
                    record.worked_hour = record.end_time - record.start_time
                search_results = self.env['hr_ethiopian_ot.rate'].search([('type', '=', 'shift')])
                if search_results:
                    record.ot_id = search_results.id
                    record.ot_type = search_results.type
                    record.rate_amount = search_results.rate
            else:
                print("Of Regular")
                works = day_periods.filtered(lambda rec: rec.name.split()[0] == record.date_name)
                end_time = sorted(works.mapped('hour_to'))
                end = 0.00
                if end_time[0] > end_time[1]:
                    end = end_time[0]
                else:
                    end = end_time[1]
                if record.start_time <= record.end_time <= end:
                    message = f"From {record.start_time} to {record.end_time} is your regular working hour."
                    record.start_time = 0.00
                    record.end_time = 0.00
                    record.user_start_time = 0.00
                    record.user_end_time = 0.00
                    raise ValidationError(_(message))
                elif record.start_time <= end < record.end_time:
                    record.start_time = end
                    record.worked_hour = record.end_time - record.start_time
                elif end < record.start_time < record.end_time:
                    record.start_time = end
                    record.worked_hour = record.end_time - record.start_time
                clause_final = [('type', '=', 'normal')]
                search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final)
                if search_results:
                    record.ot_id = search_results.id
                    record.ot_type = search_results.type
                    record.rate_amount = search_results.rate


    @api.onchange('start_time', 'end_time')
    def _onchange_days(self):
        for record in self:
            if record.start_time > 23.59 or record.end_time > 23.59:
                record.start_time = 0.00
                record.end_time = 0.00
                record.user_start_time = 0.00
                record.user_end_time = 0.00
                raise ValidationError(_('The Time You Provide Must Be Less Than 24'))
            contract = self.env['hr.contract'].search([('id', '=', record.request_id.contract_id.id), ('state', '=', 'open')])
            if contract.can_work_on_shift:
                shifts = self.env['hr.employee.shift'].search([('employee_id', '=', record.request_id.employee_id.id)])
                for shift in shifts:
                    if shift.end_date:
                        if shift.start_date <= record.date_from <= shift.end_date:
                            holiday = self.env['resource.calendar.leaves'].search([('calendar_id', '=', shift.resource_calendar_id.id), ('date_from', '<=', record.date_from), ('date_to', '>=', record.date_from)])
                            if holiday:
                                record.user_start_time = record.start_time
                                record.user_end_time = record.end_time
                                record.worked_hour = record.end_time - record.start_time
                                clause_final = [('type', '=', 'holiday')]
                                search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final)
                                if search_results:
                                    record.ot_id = search_results.id
                                    record.ot_type = search_results.type
                                    record.rate_amount = search_results.rate   
                            else:                     
                                day_periods = shift.resource_calendar_id.attendance_ids
                                self.correct_times(day_periods, record)
                        else:
                            continue
                    else:
                        if shift.start_date <= record.date_from:
                            holiday = self.env['resource.calendar.leaves'].search([('calendar_id', '=', shift.resource_calendar_id.id), ('date_from', '<=', record.date_from), ('date_to', '>=', record.date_from)])
                            if holiday:
                                record.user_start_time = record.start_time
                                record.user_end_time = record.end_time
                                record.worked_hour = record.end_time - record.start_time
                                clause_final = [('type', '=', 'holiday')]
                                search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final)
                                if search_results:
                                    record.ot_id = search_results.id
                                    record.ot_type = search_results.type
                                    record.rate_amount = search_results.rate   
                            else:                     
                                day_periods = shift.resource_calendar_id.attendance_ids
                                self.correct_times(day_periods, record)
                        else:
                            continue
            else:
                holiday = self.env['resource.calendar.leaves'].search([('calendar_id', '=', contract.resource_calendar_id.id), ('date_from', '<=', record.date_from), ('date_to', '>=', record.date_from)])
                if holiday:
                    record.user_start_time = record.start_time
                    record.user_end_time = record.end_time
                    record.worked_hour = record.end_time - record.start_time
                    clause_final = [('type', '=', 'holiday')]
                    search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final)
                    if search_results:
                        record.ot_id = search_results.id
                        record.ot_type = search_results.type
                        record.rate_amount = search_results.rate   
                else:                   
                    day_periods = contract.resource_calendar_id.attendance_ids
                    self.correct_times(day_periods, record)

    def float_to_time(float_hour):
        if float_hour == 24.0:
            return datetime.time.max
        return datetime.time(int(math.modf(float_hour)[1]), int(round(60 * math.modf(float_hour)[0], precision_digits=0)), 0)

    # @api.depends('worked_hour')
    # def _onchange_worked_hour(self):
    #     for rec in self:
    #         date = rec.date_from
    #         day_name = date.strftime('%A')
    #         clause_final = [('employee_id', '=', rec.request_id.employee_id.id),('state', '=', "open")]
    #         # resource_calendar_id = self.env['hr.contract'].search(clause_final).resource_calendar_id
    #         # clause_finalcalendar = [('calendar_id', '=', resource_calendar_id.id),("date_from", '<=' , date),("date_to",'>=' , date)]
    #         # clause_finalcalendar_attendance = [('calendar_id', '=', resource_calendar_id.id)]
    #         # search_resultsresource_calendar_id = self.env['resource.calendar.leaves'].search(clause_finalcalendar).ids
    #         can_work_on_shift = rec.request_id.contract_id.can_work_on_shift

    #         if can_work_on_shift:
    #             schedule = self.env['resource.calendar.attendance'].search(clause_finalcalendar_attendance).ids
    #             if schedule:
    #                 for period in self.env['resource.calendar.attendance'].browse(schedule):
    #                     if day_name == period.name.split()[0]:
    #                         clause_final = [('type', '=', 'shift')]
    #                         search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
    #                         if search_results:
    #                             for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
    #                                 rec.ot_id = search_result.id
    #                                 rec.ot_type = search_result.type
    #                                 rec.rate_amount = search_result.rate
    #                             return
    #                 if day_name != "Sunday" and day_name != "Saturday":
    #                     clause_final = [('type', '=', 'shift')]
    #                     search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
    #                     if search_results:
    #                         for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
    #                             rec.ot_id = search_result.id
    #                             rec.ot_type = search_result.type
    #                             rec.rate_amount = search_result.rate
    #                         return

    #         if search_resultsresource_calendar_id:
    #             clause_final = [('type', '=', 'holiday')]
    #             search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
    #             if search_results:
    #                 for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
    #                     rec.ot_id = search_result.id
    #                     rec.ot_type = search_result.type
    #                     rec.rate_amount = search_result.rate

    #                 return
    #         # elif day_name == "Sunday":
    #         #     clause_final = [('type', '=', 'sunday')]
    #         #     search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
    #         #     if search_results:
    #         #         for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
                        
    #         #             rec.ot_id = search_result.id
    #         #             rec.ot_type = search_result.type
    #         #             rec.rate_amount = search_result.rate
    #         else:
    #             clause_final = [('type', '=', 'normal')]
    #             search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
    #             if search_results:
    #                 if rec.start_time < rec.end_time:
    #                   for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
    #                     if search_result.start_time <= rec.start_time < search_result.end_time:
    #                         if search_result.start_time <= rec.end_time < search_result.end_time:
    #                             rec.ot_id = search_result.id
    #                             rec.ot_type = search_result.type
    #                             rec.rate_amount = search_result.rate
    #                             return
    #                         else:
    #                             rec.end_time = search_result.end_time
    #                             rec.ot_id = search_result.id
    #                             rec.ot_type = search_result.type
    #                             rec.rate_amount = search_result.rate
    #                             return
    #                     else:
    #                       if search_result.start_time <= rec.end_time < search_result.end_time:
    #                        rec.start_time = search_result.start_time
    #                        rec.ot_id = search_result.id
    #                        rec.ot_type = search_result.type
    #                        rec.rate_amount = search_result.rate
    #                        return
    #                 else:
    #                     raise ValidationError('The time is out of overtime range')