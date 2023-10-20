from odoo import api, fields, models


class HrEmployeeProbation(models.Model):
    _inherit = 'hr.employee'

    contract_count_non_computed = fields.Integer(String="contract count")
    
    api.onchange("contracts_count")
    def _onchange_contracts_count(self):
        for rec in self:
            print("hr contract  contract counter ")
            if rec.contracts_count:
                rec.contract_count_non_computed = rec.contracts_count
            else:
                rec.contract_count_non_computed = rec.contracts_count
            


# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


class Department(models.Model):

    _inherit = 'hr.department'

    total_employee_for_department = fields.Integer(
        compute='_compute_total_employee_for_department',store=True, string='Total Employee')

    def _compute_total_employee_for_department(self):
        emp_data = self.env['hr.employee'].read_group([('department_id', 'in', self.ids)], ['department_id'], ['department_id'])
        result = dict((data['department_id'][0], data['department_id_count']) for data in emp_data)
        for department in self:
            department.total_employee_for_department = result.get(department.id, 0)
