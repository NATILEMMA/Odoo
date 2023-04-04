# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        if not self.payslip_run_id:
            for payslip in self:
                adv_obj = self.env['salary.advance'].search(
                    [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'post')])
                input_adv = {}
                for loan in adv_obj:
                    for loan_line in loan:
                        if payslip.date_from <= loan_line.date <= payslip.date_to:
                            input_adv = {
                                'name': payslip.employee_id.name,
                                'code': "SAR",
                                'amount': loan_line.advance,
                                'contract_id': loan_line.employee_contract_id.id,
                                'payslip_id': payslip.id
                            }
                            payslip.input_line_ids.create(input_adv)

        return super(HrPayslip, self).compute_sheet()

    # def get_inputs(self, contract_ids, date_from, date_to):
    #     """This Compute the other inputs to employee payslip.
    #                        """
    #     print("get_inputs")
    #     print("contract_ids[0].id", contract_ids)
    #     if contract_ids:
    #         res = super(SalaryRuleInput, self).get_inputs(contract_ids, date_from, date_to)
    #         contract_obj = self.env['hr.contract']
    #         print("contract_ids[0].id",contract_ids)
    #         emp_id = contract_obj.browse(contract_ids[0].id).employee_id
    #         print("employee",emp_id.name)
    #         adv_salary = self.env['salary.advance'].search([('employee_id', '=', emp_id.id)])
    #         print("adv_salary",adv_salary)
    #         for adv_obj in adv_salary:
    #             current_date = date_from.month
    #             date = adv_obj.date
    #             existing_date = date.month
    #             if current_date == existing_date:
    #                 state = adv_obj.state
    #                 amount = adv_obj.advance
    #                 for result in res:
    #                     print("result",result,'state',state,'amount', amount)
    #
    #                     if state == 'posted' and amount != 0 and result.get('code') == 'SAR':
    #                         result['amount'] = amount
    #         return res


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def check(self):
        for payslip in self.slip_ids:
            adv_obj = self.env['salary.advance'].search(
                [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'post')])
            input_adv = {}
            for loan in adv_obj:
                for loan_line in loan:
                    if payslip.date_from <= loan_line.date <= payslip.date_to:
                        input_adv = {
                            'name': payslip.employee_id.name,
                            'code': "SAR",
                            'amount': loan_line.advance,
                            'contract_id': loan_line.employee_contract_id.id,
                            'payslip_id': payslip.id
                        }
                        payslip.input_line_ids.create(input_adv)

        return super(HrPayslipRun, self).check()
