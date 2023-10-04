# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        if not self.payslip_run_id:
            for payslip in self:
                print('payslip.employee_id.name', payslip.employee_id.name)
                lon_obj = self.env['hr.loan'].search(
                    [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'approve')],limit=1)
                for loan in lon_obj:
                    for loan_line in loan.loan_lines:
                        print('loan_line.date', loan_line.date)
                        if payslip.date_from <= loan_line.date <= payslip.date_to:
                            print('if')
                            input_loan = {
                                'name': payslip.employee_id.name,
                                'code': "LO",
                                'amount': loan_line.amount,
                                'contract_id': payslip.contract_id.id,
                                'payslip_id': payslip.id
                            }
                            payslip.input_line_ids.create(input_loan)
        return super(HrPayslip, self).compute_sheet()

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
