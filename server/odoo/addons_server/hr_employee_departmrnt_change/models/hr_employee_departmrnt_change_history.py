# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
# from odoo.exceptions import ValidationError



class DepartmentChangeHistory(models.Model):
    _name = 'hr.employee.departmrnt.change'
    _description = 'employee departmrnt change'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "display_name"

    display_name = fields.Char(store=False, compute="_compute_display_name", translate=True)

    employee_id = fields.Many2one('hr.employee', string='Employee', copy=False,
                                  readonly=1, states={'draft': [('readonly', False)]},
                                  help='Choose the Employee')
    
    prv_department_id = fields.Many2one('hr.department', string='Previous Department', copy=False,
                                  readonly=1,states={'draft': [('readonly', False)]}, store=True ,
                                  compute = "_compute_prv_department", help='Choose the Previous Department',)
    
    current_department_id = fields.Many2one('hr.department', string='Current Department',
                                 copy=False,
                                 readonly=1,
                                 states={'draft': [('readonly', False)]},
                                 help='Choose the current department')

    state = fields.Selection( [
                                ('draft', 'Draft'),
                                ('approved', 'Approved'),
                              ], 
                                string='Status',
                                default='draft', track_visibility='always', copy=False,
                                help='Status'
                            )
    

    def setApproved(self):
        for each in self:
            employee = self.env['hr.employee'].search([('id', '=', each.employee_id.id)])
            employee.department_id = each.current_department_id.id
            employee.write({
                'department_id': each.current_department_id.id,
                'parent_id':each.current_department_id.manager_id.id,
                })
        self.state = 'approved'

    @api.onchange('employee_id')
    def _get_lines_2(self):
        if self.employee_id:
            self.prv_department_id = self.employee_id.department_id.id    


    def setDraft(self):
        for each in self:
            employee = self.env['hr.employee'].search([('id', '=', each.employee_id.id)])
            employee.department_id = each.prv_department_id.id
            employee.write({'department_id': each.prv_department_id.id,
                            'parent_id':each.prv_department_id.manager_id.id,
                            })
        self.state = 'draft'


    @api.depends("employee_id")
    def _compute_display_name(self):
        for each in self:
            employee = self.env['hr.employee'].search([('id', '=', each.employee_id.id)])
            each.display_name = employee.name

    
    @api.depends("employee_id")
    def _compute_prv_department(self):
        for each in self:
            employee = self.env['hr.employee'].search([('id', '=', each.employee_id.id)])
            each.prv_department_id = employee.department_id.id
        



