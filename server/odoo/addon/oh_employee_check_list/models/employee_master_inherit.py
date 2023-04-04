# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeMasterInherit(models.Model):
    _inherit = 'hr.employee'

    @api.depends('job_id')
    def _compute_product_id_domain_2(self):
        for rec in self:
            rec.product_id_domain_2 = self.job_id.id
            #     json.dumps(
            #     [('document_type', '=', 'exit'), ('job_id', 'in', self.job_id.id)]
            # )

    @api.depends('job_id')
    def _compute_product_id_domain(self):
        for rec in self:
            rec.product_id_domain = self.job_id.id
            #     json.dumps(
            #     [('document_type', '=', 'entry'), ('job_id', 'in', self.job_id.id)]
            # )

    @api.depends('exit_checklist')
    def exit_progress_fun(self):
        print("each.exit_checklist")
        for each in self:
            for line in each.job_id:
                 job = each.job_id.id
            if each.job_id.id:
                total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'exit'), ('job_id', '=', job)])
                entry_len = len(each.exit_checklist)
                if total_len != 0:
                    each.exit_progress = (entry_len * 100) / total_len

    @api.onchange('job_id')
    def onchange_your_many_to_one_field(self):
         self.entry_progress_fun()
         self.exit_progress_fun()



    @api.depends('entry_checklist')
    def entry_progress_fun(self):
        print("each.entry_checklist")
        for each in self:
            for line in each.job_id:
                 job = each.job_id.id
            if each.job_id.id: 
             total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'entry'), ('job_id', '=', job)])
             entry_len = len(each.entry_checklist)
             if total_len != 0:
                each.entry_progress = (entry_len * 100) / total_len

    # name = fields.Char(translate=True)
    entry_checklist = fields.Many2many('employee.checklist', 'entry_obj', 'check_hr_rel', 'hr_check_rel',
                                       string='Entry Process', help="Entry Checklist's")
    exit_checklist = fields.Many2many('employee.checklist', 'exit_obj', 'exit_hr_rel', 'hr_exit_rel',
                                      string='Exit Process', help="Exit Checklists")
    entry_progress = fields.Float(compute=exit_progress_fun, string='Entry Progress', store=True, default=0.0,
                                  help="Percentage of Entry Checklists's")
    exit_progress = fields.Float(compute=exit_progress_fun, string='Exit Progress', store=True, default=0.0,
                                 help="Percentage of Exit Checklists's")
    maximum_rate = fields.Integer(default=100)
    check_list_enable = fields.Boolean(invisible=True, copy=False)
    product_id_domain = fields.Integer(compute="_compute_product_id_domain", readonly=True, store=False)
    product_id_domain_2 = fields.Integer(compute="_compute_product_id_domain_2", readonly=True, store=False)


class EmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    @api.model
    def create(self, vals):
        result = super(EmployeeDocumentInherit, self).create(vals)
        if result.document_name.document_type == 'entry':
            result.employee_ref.write({'entry_checklist': [(4, result.document_name.id)]})
        if result.document_name.document_type == 'exit':
            result.employee_ref.write({'exit_checklist': [(4, result.document_name.id)]})
        return result

    def unlink(self):
        for result in self:
            if result.document_name.document_type == 'entry':
                result.employee_ref.write({'entry_checklist': [(5, result.document_name.id)]})
            if result.document_name.document_type == 'exit':
                result.employee_ref.write({'exit_checklist': [(5, result.document_name.id)]})
        res = super(EmployeeDocumentInherit, self).unlink()
        return res


class EmployeeChecklistInherit(models.Model):
    _inherit = 'employee.checklist'

    entry_obj = fields.Many2many('hr.employee', 'entry_checklist', 'hr_check_rel', 'check_hr_rel',
                                 invisible=1)
    exit_obj = fields.Many2many('hr.employee', 'exit_checklist', 'hr_exit_rel', 'exit_hr_rel',
                                invisible=1)
