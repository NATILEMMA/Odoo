import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    budget_line = fields.One2many('budget.lines', 'analytic_account_id', 'Budget Lines')
    department_id = fields.Many2one('hr.department','Department')
    budget_analytic_account = fields.Boolean(default=False)
    is_allowed = fields.Boolean("Is_allowed", default=False)

class EmployeeAnalyticAccountMappingTable(models.Model):
    _name = 'hr.mapping.employee.account'

    employee_id = fields.Many2one('hr.employee')
    is_allowed = fields.Boolean("Is_allowed", default=False)
    accountAnalytic = fields.Many2one('account.analytic.account')

class Employee(models.Model):
    _inherit = 'hr.employee'

    # is_allowed = fields.Boolean("Is_allowed", default=False)
    # accountAnalytic = fields.Many2many('account.analytic.account', store=True)

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    # is_allowed = fields.Boolean("Is_allowed", default=False)
    # accountAnalytic = fields.Many2one('account.analytic.account')


class HrExpense(models.Model):

    _inherit = "hr.expense"
    # analytic_account_id = fields.Many2one('account.analytic.account', required=True)

    


    @api.model
    def create(self, vals):
        _logger.info("############ Expensse vals:%s",vals)
        user = self.env['res.users'].search([('id','=',self.env.uid)])
        employee_id = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
        AccountAnalytic = self.env['account.analytic.account'].search([('id','=',vals['analytic_account_id'])], limit=1)
        search_mapping = self.env['hr.mapping.employee.account'].search([('employee_id','=',employee_id.id),('accountAnalytic','=',AccountAnalytic.id)], limit=1)
        reserved_amounts = []
        try:
            product_account = self.env['product.product'].search([('id','=',vals['product_id'])], limit=1)
            budget = self.env['budget.planning'].search([('analytic_account_id','=',AccountAnalytic.id)], limit=1)
            to_budget = self.env['budget.budget'].search([('name','=',budget.name)], limit=1)
            for x in to_budget.budget_line:
                for bline in x.general_budget_id.account_ids:
                    if product_account.property_account_expense_id.id == bline.id:
                        reserved_amounts.append(x.reserved_amount)
        except:
            pass
        fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)

        # try:
        if AccountAnalytic.budget_analytic_account == True:
            try:
                if search_mapping:
                    # if AccountAnalytic.is_allowed == True:
                    _logger.info("TTTTTTTTTTTTTTTTTTT")
                    total_request = float(vals['unit_amount']) * float(vals['quantity'])
                    reserved_amounts = reserved_amounts[0] 
                    if  search_mapping.is_allowed == True: #AccountAnalytic.department_id == employee_id.department_id and
                        _logger.info("$$$$$$")
                        if len(fiscal_year) > 0:
                            if str(fiscal_year.date_from) < vals['date'] < str(fiscal_year.date_to):

                                if float(total_request) <= float(reserved_amounts):
                                    pass
                                else:
                                    # raise Warning("Your requested amount: is greater than the amount specified in the budget code.")
                                    raise Warning("Your requested amount: " +str(total_request)+ " is greater than the amount specified in the budget code.")

                                # raise Warning("passed")
                            else:
                                raise Warning("Select the appropriate fiscal date for your Expense.")
                        else:
                            raise UserError(_('Fiscal year of the system is not set.'))

                    else:
                        raise UserError(_('This account has not been approved, and the budget approval process has not been completed.'))
                        raise UserError(_('You are not authorized to use this budget account.'))
                else:
                    raise UserError(_('You are not authorized to use this budget account.'))

                    

            except Exception as e:
                _logger.warning("Cannot duplicate!", exc_info=True)
                raise ValidationError(e)
        else:
            pass
        # except:
        #     raise UserError(_('Fiscal year of the system is not set.'))


            # raise Warning("Your Are  Allowed For This Budget Account")
        return super(HrExpense, self).create(vals)


    def write(self, vals):
        _logger.info("############ Expense Update:%s",vals)
        try:
            employee_id = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
            AccountAnalytic = self.env['account.analytic.account'].search([('id','=',vals['analytic_account_id'])], limit=1)
            search_mapping = self.env['hr.mapping.employee.account'].search([('employee_id','=',employee_id.id),('accountAnalytic','=',AccountAnalytic.id)], limit=1)
            reserved_amounts = []
            try:
                product_account = self.env['product.product'].search([('id','=',vals['product_id'])], limit=1)
                budget = self.env['budget.planning'].search([('analytic_account_id','=',AccountAnalytic.id)], limit=1)
                to_budget = self.env['budget.budget'].search([('name','=',budget.name)], limit=1)
                for x in to_budget.budget_line:
                    for bline in x.general_budget_id.account_ids:
                        if product_account.property_account_expense_id.id == bline.id:
                            reserved_amounts.append(x.reserved_amount)
            except:
                pass
            fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)

            # try:
            if AccountAnalytic.budget_analytic_account == True:
                try:
                    if search_mapping:
                        # if AccountAnalytic.is_allowed == True:
                        _logger.info("TTTTTTTTTTTTTTTTTT")
                        total_request = float(vals['unit_amount']) * float(vals['quantity'])
                        reserved_amounts = reserved_amounts[0] 
                        if  search_mapping.is_allowed == True: #AccountAnalytic.department_id == employee_id.department_id and
                            _logger.info("$$$$$$")
                            if len(fiscal_year) > 0:
                                if str(fiscal_year.date_from) < vals['date'] < str(fiscal_year.date_to):

                                    if float(total_request) <= float(reserved_amounts):
                                        pass
                                    else:
                                        # raise Warning("Your requested amount: is greater than the amount specified in the budget code.")
                                        raise Warning("Your requested amount: " +str(total_request)+ " is greater than the amount specified in the budget code.")

                                    # raise Warning("passed")
                                else:
                                    raise Warning("Select the appropriate fiscal date for your Expense.")
                            else:
                                raise UserError(_('Fiscal year of the system is not set.'))

                        else:
                            raise UserError(_('This account has not been approved, and the budget approval process has not been completed.'))
                            raise UserError(_('You are not authorized to use this budget account.'))
                    else:
                        raise UserError(_('You are not authorized to use this budget account.'))

                        

                except Exception as e:
                    _logger.warning("Cannot duplicate!", exc_info=True)
                    raise ValidationError(e)
            else:
                pass
        except:
            pass

        return super(HrExpense, self).write(vals)

