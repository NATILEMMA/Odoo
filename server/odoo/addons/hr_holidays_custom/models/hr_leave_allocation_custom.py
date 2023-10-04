"""This function will customize the hr leave allocation"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'


    for_leave_type = fields.Selection(selection=[('annual', 'Annual Leave'), ('other', 'Other...')], default='other')
    expired_date = fields.Date(string="Expires On", readonly=True, store=True)
    end_of_year_reminder = fields.Date(string="Reminder for Next Year", store=True)
    total_working_days = fields.Integer(string="Total Working Days", readonly=True, store=True)
    total_working_months = fields.Integer(string="Total Working Months", readonly=True, store=True)
    total_working_years = fields.Integer(string="Total Working Years", readonly=True, store=True)
    for_annual_leave_allowed = fields.Selection(selection=[('annual', 'Annual Leave')])

    def update_leave(self):
        """This function will send message to hr when employee's year is due"""
        approved_ids = self.env['hr.leave.allocation'].search([('state', '=', 'validate'), ('end_of_year_reminder', '=', date.today())])
        for approved in approved_ids:
            hr_partner = approved.employee_id.contract_id.hr_responsible_id
            employee = approved.employee_id
            remaining = employee.remaining_leaves
            approved.write({'state': 'confirm'})
            message = f"Please update {approved.employee_id.name}'s annual leave."
            model = self.env['ir.model'].search([('model', '=', 'hr.leave.allocation'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Time Off Approval')], limit=1)
            self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Leave Update",
                'date_deadline': date.today() + relativedelta(weeks=2),
                'user_id': hr_partner.id,
                'res_model_id': model.id,
                'res_id': approved.id,
                'activity_type_id': activity_type.id
            })
            hr_partner.notify_warning(message, '<h4>Update Leave</h4>', True)


    def create_new_leave(self):
        """This function will send message to hr when leave expires"""
        approved_ids = self.env['hr.leave.allocation'].search([('state', '=', 'validate'), ('expired_date', '=', date.today())])
        for approved in approved_ids:
            hr_partner = approved.employee_id.contract_id.hr_responsible_id
            hr_partner = approved.employee_id.contract_id.hr_responsible_id
            if not hr_partner:
                raise UserError(_("Please Add Hr Responsible for this Employee's Contract"))
            employee = approved.employee_id
            start_date = date.today()
            approved.write({'state': 'refuse'})
            message = f"Please create {approved.employee_id.name}'s leave."
            model = self.env['ir.model'].search([('model', '=', 'hr.leave.allocation'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Time Off Approval')], limit=1)
            self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Leave Renewal",
                'date_deadline': start_date + relativedelta(weeks=2),
                'user_id': hr_partner.id,
                'res_model_id': model.id,
                'res_id': approved.id,
                'activity_type_id': activity_type.id
            })
            hr_partner.notify_warning(message, '<h4>Create New Leave</h4>', True)


    def send_notification_to_management(self):
        """This function will send message to management regarding employees leave"""
        two_month_from_today = date.today() + relativedelta(months=2)
        approved_ids = self.env['hr.leave.allocation'].search([('state', '=', 'validate'), ('expired_date', '=', two_month_from_today)])
        for approved in approved_ids:
            hr_partner = approved.employee_id.contract_id.hr_responsible_id
            if not hr_partner:
                raise UserError(_("Please Add Hr Responsible for this Employee's Contract"))
            remaining = approved.employee_id.remaining_leaves
            if remaining > 0:
                new_message = f"Please discuss with {hr_partner.name} about your remaing {remaining} leave days that are about to expire on {two_month_from_today}."
                approved.employee_id.user_id.notify_warning(new_message, '<h4>Leave Expiry Meeting</h4>', True)
                message = f"Please discuss with {approved.employee_id.name} about the remaining leaves before it expires on {two_month_from_today}."
                model = self.env['ir.model'].search([('model', '=', 'hr.leave.allocation'), ('is_mail_activity', '=', True)])
                activity_type = self.env['mail.activity.type'].search([('category', '=', 'meeting')], limit=1)
                approved.write({'state': 'confirm'})
                self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Leave Expiry Meeting",
                    'date_deadline': two_month_from_today,
                    'user_id': hr_partner.id,
                    'res_model_id': model.id,
                    'res_id': approved.id,
                    'activity_type_id': activity_type.id
                })
                hr_partner.notify_warning(message, '<h4>Create New Leave</h4>', True)


    def set_annual_leave(self):
        """This function is going to retrieve the contract of employee and get the number of woring days"""
        for record in self:
            record.for_annual_leave_allowed = 'annual'
            contract = self.env['hr.contract'].search([('employee_id', '=', record.employee_id.id), ('state', '=', 'open')])
            if len(contract) > 1 or not contract:
                raise UserError(_('Selected employee has multiple or no running contracts!'))
            if record.employee_id and record.for_leave_type == 'annual':
                today_date = date.today()
                
                start_date = None
                if contract.trial_date_end: start_date = contract.trial_date_end 
                else: start_date = contract.date_start

                total_days = (today_date - start_date).days
                record.total_working_years, total_days = total_days // 365, total_days % 365
                record.total_working_months, total_days = total_days // 30, total_days % 30
                record.total_working_days = total_days
                if contract.start_date_for_approval:
                    record.expired_date = contract.start_date_for_approval + relativedelta(years=2)
                    record.end_of_year_reminder = contract.start_date_for_approval + relativedelta(years=1)
                    contract.start_date_for_approval = record.end_of_year_reminder
                                       
                else:
                    record.expired_date = start_date + relativedelta(years=2)
                    record.end_of_year_reminder = start_date + relativedelta(years=1)
                    contract.start_date_for_approval = record.end_of_year_reminder