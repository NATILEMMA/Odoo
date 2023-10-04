# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import except_orm
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class SalaryAdvancePayment(models.Model):
    _name = "salary.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', readonly=True, default=lambda self: 'Adv/',translate=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, help="Employee")
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(), help="Submit date")
    reason = fields.Text(string='Reason', help="Reason",translate=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Advance', required=True)
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    exceed_condition = fields.Boolean(string='Exceed than Maximum',
                                      help="The Advance is greater than the maximum percentage in salary structure")
    department = fields.Many2one('hr.department', string='Department')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('waiting_approval', 'Waiting Approval'),
                              ('approve', 'Approved'),
                              ('post', 'Posted'),
                              ('cancel', 'Cancelled'),
                              ('reject', 'Rejected')], string='Status', default='draft', track_visibility='onchange')
    debit = fields.Many2one('account.account', string='Debit Account')
    credit = fields.Many2one('account.account', string='Credit Account')
    journal = fields.Many2one('account.journal', string='Journal')
    employee_contract_id = fields.Many2one('hr.contract', string='Contract')
    move_id = fields.Many2one('account.move', string="Journal Entery")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        department_id = self.employee_id.department_id.id
        domain = [('employee_id', '=', self.employee_id.id)]
        self.department = department_id
        self.employee_contract_id = self.employee_id.contract_id.id
        if self.employee_id.contract_id.no_pention:
            raise ValidationError(_('Only permanent employee can take loan advance'))
        print("self.employee_id", self.employee_id.id)
        if not self.employee_id.contract_id:
           if self.employee_id.id:
             raise ValidationError(_('employee has no contract'))
        if self.employee_id.contract_id.state != 'open':
            if self.employee_id.id:
                raise ValidationError(_('employee contract is not open'))
        return {'value': {'department': department_id}, 'domain': {
            'employee_contract_id': domain,
        }}

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal': domain,
            },

        }
        return result

    def submit_to_manager(self):
        self.state = 'submit'

    def cancel(self):
        self.state = 'cancel'

    def reject(self):
        self.state = 'reject'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('salary.advance.seq') or ' '
        res_id = super(SalaryAdvancePayment, self).create(vals)
        return res_id

    def approve_request(self):
        """This Approve the employee salary advance request.
                   """
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_home_id
        if not address.id:
            raise except_orm('Error!',
                             'Define home address for the employee. i.e address under private information of the employee.')
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise except_orm('Error!', 'Advance can be requested once in a month')
        if not self.employee_contract_id:
            raise except_orm('Error!', 'Define a contract for the employee')
        struct_id = self.employee_contract_id.struct_id
        adv = self.advance
        amt = self.employee_contract_id.wage
        if adv > amt and not self.exceed_condition:
            raise except_orm('Error!', 'Advance amount is greater than allotted')
        avr = self.env['salary.advance.conf'].search([])
        if not avr.percent or avr.percent == 0:
            raise except_orm('Error!', 'Set Salary advance rule')
        percent = (avr.percent* amt)/100
        if adv > percent:
                raise except_orm('Error!', 'Advance amount is greater than '+str(30)+ '% of the wage of employee')
        if not self.advance:
            raise except_orm('Warning', 'You must Enter the Salary Advance amount')
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise except_orm('Warning', "This month salary already calculated")

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('Request can be done after "%s" Days From prevoius month salary') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        self.state = 'approve'

    def post_request(self):
        date = datetime.now()
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
        if not active_time_frame.id:
            raise ValidationError(_(
                'please set Time frame for the journal'))
        active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if not active_fiscal_year.id:
            raise ValidationError(_(
                'please set Active fiscal year for the journal'))
        time_frame = active_time_frame.id
        fiscal_year = active_fiscal_year.id
        """This Approve the employee salary advance request from accounting department.
                   """
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise except_orm('Error!', 'Advance can be requested once in a month')
        if not self.debit or not self.credit or not self.journal:
            raise except_orm('Warning', "You must enter Debit & Credit account and journal to approve ")
        if not self.advance:
            raise except_orm('Warning', 'You must Enter the Salary Advance amount')

        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            reference = request.name
            journal_id = request.journal.id
            move = {
                'narration': 'Salary Advance Of ' + request_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'fiscal_year': fiscal_year,
                'time_frame': time_frame,
                'partner_id': self.employee_id.address_home_id.id,
            }

            debit_account_id = request.debit.id
            credit_account_id = request.credit.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': request_name,
                    'account_id': debit_account_id,
                    'partner_id': self.employee_id.address_home_id.id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': request_name,
                    'account_id': credit_account_id,
                    'partner_id': self.employee_id.address_home_id.id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move.update({'line_ids': line_ids})
            print("move.update({'line_ids': line_ids})", move.update({'invoice_line_ids': line_ids}))
            draft = move_obj.create(move)
            self.move_id = draft.id
            self.state = 'post'
            return True
class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    salary_advance_ids = fields.One2many("salary.advance","employee_id",string="Salary Advance")
    salary_advance_request_count = fields.Integer(compute='_compute_advance_count', string='Request Count')

    @api.depends('salary_advance_ids')
    def _compute_advance_count(self):
        for request in self:
            request.salary_advance_request_count = len(request.salary_advance_ids)