
from odoo import tools
import re
import base64
import requests
import babel
from collections import defaultdict
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from pytz import utc

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
import logging, pprint
_logger = logging.getLogger(__name__)

# This will generate 16th of days
ROUNDING_FACTOR = 16



class HrAttendanceAbsetn(models.Model):
    _name = 'hr.attendance.absent'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date(string="Absent Date")
    month_y = fields.Char()


    def action_absent_employee(self,compute_leaves=True, calendar=None, domain=None):
        all_employee=self.env['hr.employee'].search([])
        for obj in all_employee:
            resource = obj
            calendar = obj.resource_calendar_id
            current_mon = datetime.now().month
            current_year =  datetime.now().year
            current_date =  datetime.now().day
            current_date = date(current_year,current_mon,current_date)

            check_date = date(current_year,current_mon, 1)
            _logger.info(check_date)

            number_of_days = current_date - check_date
            number_of_days = str(number_of_days).split(' ')
            _logger.info("#### number_of_days:%s",number_of_days[0])
            date_list = []
            too_datetime = []
            ### Generating Month dates 
            for da in range(int(number_of_days[0])+1):
                a_date = (check_date + timedelta(days = da)).isoformat()
                date_list.append(a_date)
            from_datetime = date_list[0]
            to_datetime = date_list[-1]
            from_datetime = datetime.combine(fields.Date.from_string(from_datetime), time.min)
            to_datetime = datetime.combine(fields.Date.from_string(to_datetime), time.max)
            if not from_datetime.tzinfo:
                from_datetime = from_datetime.replace(tzinfo=utc)
            if not to_datetime.tzinfo:
                to_datetime = to_datetime.replace(tzinfo=utc)

            # total hours per day: retrieve attendances with one extra day margin,
            # in order to compute the total hours on the first and last days
            from_full = from_datetime - timedelta(days=1)
            to_full = to_datetime + timedelta(days=1)
            intervals = calendar._attendance_intervals(from_full, to_full, resource)
            day_total = defaultdict(float)
            for start, stop, meta in intervals:
                day_total[start.date()] += (stop - start).total_seconds() / 3600

            # actual hours per day
            if compute_leaves:
                intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain)
            else:
                intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource)
            day_hours = defaultdict(float)
            for start, stop, meta in intervals:
                day_hours[start.date()] += (stop - start).total_seconds() / 3600

            # compute number of days as quarters
            _logger.info("ROUNDING_FACTOR %s",ROUNDING_FACTOR)
            # _logger.info("day_hours[day] %s",day_hours[day])
            
            days = sum(
                float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
                for day in day_hours
            )
            ttyme = datetime.combine(fields.Date.from_string(datetime.now()), time.min)
            _logger.info(ttyme)
            locale = self.env.context.get('lang') or 'en_US'
            month_y = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))

            get_attendance_hours = self.env['hr.attendance.filtered'].search([
                    ('month_y', '=', month_y)
                ], order='check_in desc')
            for day in day_hours:
                for obj in all_employee:
                    check_contract_status = self.env['hr.contract'].search([('id','=',obj.resource_id.id),('state','=','open')], limit=1)

                    if not check_contract_status:
                        continue
                    else:
                        check_log_before_absent = self.env['hr.attendance.filtered'].search([
                        ('employee_id', '=', obj.id),
                        ('date', '=', day)
                        ], limit=1)
                        if not check_log_before_absent:
                            check_specail_case_absent_report = self.env['specail.case.absent'].search([
                                ('employee_id', '=', obj.id),
                                ('date_from', '=', day),('state','=','approved')
                                ], limit=1)
                            if not check_specail_case_absent_report:
                                check_absent_record=self.env['hr.attendance.absent'].search([('employee_id','=',obj.id),('date','=',day)],limit=1)
                                # _logger.info("check_absent_record %s",check_absent_record)
                                if not check_absent_record:
                                    ttyme = datetime.combine(fields.Date.from_string(day), time.min)
                                    locale = self.env.context.get('lang') or 'en_US'
                                    monthY = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))
                                    create_absent = check_absent_record.create({
                                        'employee_id': obj.id,
                                        'date': day,
                                        'month_y': monthY
                                    })
                                    _logger.info("^^^^ create_absent %s",create_absent)
                                else:
                                   continue
                            else:
                                _logger.info(" ################# Absent recorded on specail Case report  ############")
                                for val in check_specail_case_absent_report:
                                    durations = []
                                    if val.date_to  == val.date_from:
                                        durations.append(0)
                                    else:
                                        date_duration = val.date_to - val.date_from
                                        duration = str(date_duration).split(' ')
                                        durations.append(duration[0])
                                    for loop in range(int(durations[0])):
                                        date_from = (val.date_from + timedelta(days = loop)).isoformat()
                                        check_absent_record=self.env['hr.attendance.absent'].search([('employee_id','=',obj.id),('date','=',date_from)],limit=1)
                                        if check_absent_record:
                                            month_days = datetime.strptime(date_from,'%Y-%m-%d')
                                            attended_check_in = month_days.replace(hour=5,minute=30,second=0)
                                            attended_check_out = month_days.replace(hour=13,minute=30,second=0)
                                            # _logger.info(" ^^^^^^^^^^^ attended_check_in:%s",attended_check_in)
                                            # _logger.info("  ^^^^^^^^^^^ attended_check_out:%s",attended_check_out)

                                            attended = check_log_before_absent.sudo().create({
                                                'date': date_from,
                                                'month_y': check_specail_case_absent_report.month_y,
                                                'employee_id': check_specail_case_absent_report.employee_id.id,
                                                'check_in': attended_check_in,
                                                'check_out': attended_check_out,
                                            })
                                            _logger.info(" ################# attended %s",attended)
                                            check_absent_record.unlink()
                                        else:
                                            month_days = datetime.strptime(date_from,'%Y-%m-%d')
                                            attended_check_in = month_days.replace(hour=8,minute=30,second=0)
                                            attended_check_out = month_days.replace(hour=16,minute=30,second=0)
                                            attended = check_log_before_absent.sudo().create({
                                                'date': date_from,
                                                'month_y': check_specail_case_absent_report.month_y,
                                                'employee_id': check_specail_case_absent_report.employee_id.id,
                                                'check_in': attended_check_in,
                                                'check_out': attended_check_out,
                                            })
                                            _logger.info(" ################# attended %s",attended)
                                            
                        else:
                            _logger.info(" ################# Present ############")
                            continue
            self.check_finaly_absent_employee();       
            return True
        
    
    def check_finaly_absent_employee(self,compute_leaves=True, calendar=None, domain=None):
        all_employee=self.env['hr.employee'].search([])

        for obj in all_employee:
            resource = obj
            calendar = obj.resource_calendar_id
            current_mon = datetime.now().month
            current_year =  datetime.now().year
            current_date =  datetime.now().day
            current_date = date(current_year,current_mon,current_date)
            check_date = date(current_year,current_mon, 1)
            number_of_days = current_date - check_date
            number_of_days = str(number_of_days).split(' ')
            date_list = []
            for da in range(int(number_of_days[0])+1):
                a_date = (check_date + timedelta(days = da)).isoformat()
                date_list.append(a_date)
            from_datetime = date_list[0]
            to_datetime = date_list[-1]
            from_datetime = datetime.combine(fields.Date.from_string(from_datetime), time.min)
            to_datetime = datetime.combine(fields.Date.from_string(to_datetime), time.max)

            if not from_datetime.tzinfo:
                from_datetime = from_datetime.replace(tzinfo=utc)
            if not to_datetime.tzinfo:
                to_datetime = to_datetime.replace(tzinfo=utc)

            # total hours per day: retrieve attendances with one extra day margin,
            # in order to compute the total hours on the first and last days
            from_full = from_datetime - timedelta(days=1)
            to_full = to_datetime + timedelta(days=1)
            intervals = calendar._attendance_intervals(from_full, to_full, resource)
            day_total = defaultdict(float)
            for start, stop, meta in intervals:
                day_total[start.date()] += (stop - start).total_seconds() / 3600

            # actual hours per day
            if compute_leaves:
                intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain)
            else:
                intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource)
            day_hours = defaultdict(float)
            for start, stop, meta in intervals:
                day_hours[start.date()] += (stop - start).total_seconds() / 3600

            days = sum(
                float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
                for day in day_hours
            )
            ttyme = datetime.combine(fields.Date.from_string(datetime.now()), time.min)
            _logger.info(ttyme)
            locale = self.env.context.get('lang') or 'en_US'
            month_y = tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))
            get_attendance_hours = self.env['hr.attendance.filtered'].search([
                    ('month_y', '=', month_y)
                ], order='check_in desc')
            for day in day_hours:
                for obj in all_employee:
                    check_contract_status = self.env['hr.contract'].search([('id','=',obj.resource_id.id),('state','=','open')], limit=1)
                    if not check_contract_status:
                       continue
                    else:
                        check_absent_record=self.env['hr.attendance.absent'].search([('employee_id','=',obj.id),('date','=',day)],limit=1)      
                        calendar_resource = self.env['resource.calendar'].search([
                                ('id', '=', obj.resource_calendar_id.id)
                                ])
                        if not calendar_resource:
                            continue
                        else:
                            holiday_duration = calendar_resource.global_leave_ids.date_to - calendar_resource.global_leave_ids.date_from
                            holiday_duration = str(holiday_duration).split(' ')[0]     
                            h_dur = []
                            for holiday in range(int(holiday_duration)):
                                H_date = (calendar_resource.global_leave_ids.date_from.date() + timedelta(days = holiday)).isoformat()
                                h_dur.append(H_date)
                            for hd in h_dur:
                                if str(day) ==str(hd):
                                    check_absent_record.unlink()
                                else:
                                    continue

                            
                            # """
                            #     Checking on Hr Leave/ timeoff 
                            #     if the leave are on no_Validation timeoff type ; take the that date as attende value
                            #     else the timeoff type are no_validation timeoff type check on approval of hr before take as attend
                            # """
                            filter_timeoff_type = self.env['hr.leave.type'].search([('validation_type','!=','no_validation')])
                            no_validation_timeoff_type = self.env['hr.leave.type'].search([('validation_type','=','no_validation')])
                            timeoff_type = []
                            no_validation_type = []
                            for tot in filter_timeoff_type:
                                timeoff_type.append(tot.id)
                            for NoV in no_validation_timeoff_type:
                                no_validation_type.append(NoV.id)
                            check_hr_leave = self.env['hr.leave'].search([('employee_id','=',obj.id),('holiday_status_id','in',timeoff_type),('state','=','validate')])
                            no_validation_hr_leave = self.env['hr.leave'].search([('employee_id','=',obj.id),('holiday_status_id','in',no_validation_type),('payslip_status','=',True)])
                            for leave in check_hr_leave:
                                ldate_dur = leave.date_to - leave.date_from  
                                ldate = str(ldate_dur).split(' ')[0]
                                leave_dur = []
                                for l in range(int(ldate)):
                                    L_date = (leave.date_from.date() + timedelta(days = l)).isoformat()
                                    leave_dur.append(L_date)
                                for ld in leave_dur:
                                    if str(day) ==str(ld):
                                        check_absent_record.unlink()
                                    else:
                                        continue
                            for n in no_validation_hr_leave:
                                nodate_dur = n.date_to - n.date_from  
                                ndate = str(nodate_dur).split(' ')[0]
                                n_dur = []
                                for nn in range(int(ndate)+1):
                                    n_date = (n.date_from.date() + timedelta(days = nn)).isoformat()
                                    n_dur.append(n_date)
                                for nol in n_dur:
                                    if str(day) ==str(nol):
                                        check_absent_record.unlink()
                                    else:
                                        continue




    