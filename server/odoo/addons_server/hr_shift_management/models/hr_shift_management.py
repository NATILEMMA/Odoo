"""This file will handle shift managements"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError 
from datetime import timedelta

class HrEmployeeShifts(models.Model):
    _name="hr.employee.shift"
    _description="This class will create shifts for each employees"

    name = fields.Char(required=True, translate=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Schedule", readonly=True)
    start_date = fields.Date(string="Shift Start Date", readonly=True)
    end_date = fields.Date(string="Shift End Date", readonly=True)
    state = fields.Selection(selection=[('open', 'Open'), ('closed', 'Closed')], string="State", readonly=True)


class HrEmployeeCustom(models.Model):
    _inherit='hr.employee'

    shift_ids = fields.One2many('hr.employee.shift', 'employee_id', readonly=True)


class HrShiftManagement(models.Model):
    _name="hr.shift.management"
    _description="This class will handle the shift managements"


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New',translate=True)
    start_date = fields.Date()
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', store=True, required=True)

    employee_ids = fields.Many2many('hr.employee', domain=[('contract_id.state', '=', 'open')], store=True)
    end_date = fields.Date()
    state = fields.Selection(selection=[('open', 'Open'), ('closed', 'Closed')], string="State", default='open')


    @api.onchange('resource_calendar_id')
    def _get_all_employees(self):
        """This function will get all employees who are on the same shift"""
        for record in self:
            contract_ids = self.env['hr.contract'].search([('resource_calendar_id', '=', record.resource_calendar_id.id), ('state', '=', 'open')])
            employees = contract_ids.mapped('employee_id').ids
            record.employee_ids = [(6, 0, employees)]


    @api.model
    def create(self, vals):
        """This function will create employee shifts"""
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.shift.management')
        schedule = super(HrShiftManagement, self).create(vals)
        open_shift = self.env['hr.shift.management'].search([('resource_calendar_id', '=', schedule.resource_calendar_id.id), ('state', '=', 'open'), ('create_date', '!=', schedule.create_date)])
        delta = timedelta(days=1)
        if open_shift:
            open_shift.state = 'closed'
            open_shift.end_date = schedule.start_date - delta
            # open_shift.end_date = schedule.create_date
        for employee in schedule.employee_ids:
            employee.contract_id.resource_calendar_id = schedule.resource_calendar_id
            if len(employee.shift_ids.ids) > 0:
                shift = self.env['hr.employee.shift'].search([('employee_id', '=', employee.id), ('end_date', '=', False)])
                shift.end_date = schedule.start_date - delta
                # shift.end_date = schedule.create_date.strftime('%Y-%m-%d')
                shift.state = 'closed'
                self.env['hr.employee.shift'].sudo().create({
                    'name': schedule.name,
                    'employee_id': employee.id,
                    'resource_calendar_id': schedule.resource_calendar_id.id,
                    'start_date': schedule.start_date,
                    # 'start_date': schedule.create_date.strftime('%Y-%m-%d'),
                    'state': schedule.state
                })
            else:
                self.env['hr.employee.shift'].sudo().create({
                    'name': schedule.name,
                    'employee_id': employee.id,
                    'resource_calendar_id': schedule.resource_calendar_id.id,
                    'start_date': schedule.start_date,
                    # 'start_date': schedule.create_date.strftime('%Y-%m-%d'),
                    'state': schedule.state
                })
        return schedule
