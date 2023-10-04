# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _name = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees')

    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            contract = self.env['hr.contract'].search([('employee_id', '=', employee.id)], limit=1)
            if contract.state == 'open':
                res = {
                    'employee_id': employee.id,
                    'name': contract.name,
                    'struct_id': contract.struct_id.id,
                    'contract_id': contract.id,
                    'payslip_run_id': active_id,
                    # 'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    # 'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from': from_date,
                    'date_to': to_date,
                    'credit_note': run_data.get('credit_note'),
                    'company_id': employee.company_id.id,
                }
                payslips += self.env['hr.payslip'].create(res)
        return {'type': 'ir.actions.act_window_close'}
