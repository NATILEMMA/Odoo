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

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    budget_line_code = fields.Many2one('account.budget.post')

    # @api.model
    # def create(self,vals):
        # _logger.info("^^^^^^^^^^^^^^AccountATTTTTTTTTTTTTTTTTTTTTnalyticLine^^^^^^^^^^^^^^%s",vals)
        # _logger.info(vals['account_id']) 
        # account = self.env['account.analytic.account'].search([('id','=',vals['account_id'])], limit=1)
        # budget_code = []
        # _logger.info("sssssssssssssssss %s",self.id)
        # _logger.info("sssssssssssssssss %s",self.account_id)
        # _logger.info("sssssssssssssssss %s",self.account_id.name)
        # _logger.info("sssssssssssssssss %s",self.amount)



        # _logger.info("sssssssssssssssss %s",self.line_ids)

        # for line in self.line_ids:

        #     account = line.analytic_account_id.name
        #     if account != False:
        #         budget =  self.env["budget.budget"].search([('name','=',line.analytic_account_id.name)], limit=1)
        #         for l in budget.budget_line.general_budget_id:
        #             for loop in l.account_ids:
        #                 if line.account_id.id == loop.id:
        #                     budget_code.append(l.id)
        #                     line.budget_line_code = l.id
        #                 else:
        #                     continue
        #     else:
        #         pass

        # _logger.info("Budget_code:%s",budget_code[0])
        # return super(AccountAnalyticLine, self).create(vals)




class AccountMove(models.Model):
    _inherit = "account.move"
    is_budget_transfer_journal = fields.Boolean()


    def action_post(self):
        budget_code = []
        for line in self.line_ids:
            account = line.analytic_account_id.name
            try:
                if account != False:
                    budget =  self.env["budget.budget"].search([('name','=',line.analytic_account_id.name)], limit=1)
                    for l in budget.budget_line.general_budget_id:
                        for loop in l.account_ids:
                            if line.account_id.id == loop.id:
                                budget_code.append(l.id)
                                if len(line.budget_line_code) > 0:
                                    pass
                                else:
                                    line.budget_line_code = l.id
                            else:
                                continue
                else:
                    pass
            except:
                pass
        return super(AccountMove, self).action_post()






class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    budget_line_code = fields.Many2one('account.budget.post')
    amount = fields.Monetary(string='Balance', store=True,)


    

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    budget_line = fields.One2many('budget.lines', 'analytic_account_id', 'Budget Lines')
    department_id = fields.Many2one('hr.department','Department')
    budget_analytic_account = fields.Boolean(default=False)
    is_allowed = fields.Boolean("Is_allowed", default=False)


    # @api.model
    # def create(self,vals):
    #     _logger.info("^^^^^^^^^^^^^^AccountAnalyticLine^^^^^^^^^^^^^^%s",vals)


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
    analytic_account_id = fields.Many2one('account.analytic.account', required=True, domain="[('budget_analytic_account', '=', True)]")

    

    @api.model
    def create(self, vals):
        _logger.info("############ Expensse vals:%s",vals)
        user = self.env['res.users'].search([('id','=',self.env.uid)])
        employee_id = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
        AccountAnalytic = self.env['account.analytic.account'].search([('id','=',vals['analytic_account_id'])], limit=1)
        search_mapping = self.env['hr.mapping.employee.account'].search([('employee_id','=',employee_id.id),('accountAnalytic','=',AccountAnalytic.id)], limit=1)
        reserved_amounts = []
        budget_codes = []
        product_account_code = []
        try:
            product_account = self.env['product.product'].search([('id','=',vals['product_id'])], limit=1)
            budget = self.env['budget.planning'].search([('analytic_account_id','=',AccountAnalytic.id)], limit=1)
            to_budget = self.env['budget.budget'].search([('name','=',budget.name)], limit=1)
            for x in to_budget.budget_line:
                for bline in x.general_budget_id.account_ids:
                    if product_account.property_account_expense_id.id == bline.id:
                        reserved_amounts.append(x.reserved_amount)
                    budget_codes.append(bline.id)
            product_account_code.append(product_account.property_account_expense_id.id)

           
        except:
            pass
        fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)

        # try:
        if AccountAnalytic.budget_analytic_account == True:
            try:
                if search_mapping:
                    # if AccountAnalytic.is_allowed == True:
                    _logger.info("TTTTTTTTTTTTTTTTTTT")
                    _logger.info("TTTTTTTTTTTTTTTTTTT %s",product_account_code)

                    _logger.info("TTTTTTTTTTTTTTTTTTT %s",budget_codes)
                    _logger.info("TTTTTTTTTTTTTTTTTTT %s",reserved_amounts)


                    total_request = float(vals['unit_amount']) * float(vals['quantity'])
                   
                    if product_account_code[0] in budget_codes:
                        reserved_amounts = reserved_amounts[0] 
                        if  search_mapping.is_allowed == True: #AccountAnalytic.department_id == employee_id.department_id and
                            _logger.info("$$$$$$")
                            if len(fiscal_year) > 0:
                                if str(fiscal_year.date_from) < vals['date'] < str(fiscal_year.date_to):

                                    if float(total_request) <= float(reserved_amounts):
                                        pass
                                    else:
                                        # raise Warning("Your requested amount: is greater than the amount specified in the budget code.")
                                        raise Warning(_('Your requested amount:%s is greater than the amount specified in the budget code.')  %(str(total_request)))

                                    # raise Warning("passed")
                                else:
                                    raise Warning(_("Select the appropriate fiscal date for your Expense."))
                            else:
                                raise UserError(_('Fiscal year of the system is not set.'))

                        else:
                            raise UserError(_('This account has not been approved, and the budget approval process has not been completed.'))
                    else:
                        raise UserError(_('The Expense Account are not in this budget code...\n Please ckeck your product Expense Account'))
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
        _logger.info("############ Expensse vals:%s",vals)
        user = self.env['res.users'].search([('id','=',self.env.uid)])
       
        # try:
        AccountAnalytics = []
        reserved_amounts = []
        budget_codes = []
        product_account_code = []
        employee_id = self.env['hr.employee'].search([('id','=',user.employee_id.id)])
        try:
            if  vals['analytic_account_id'] is not None:
                AccountAnalytic = self.env['account.analytic.account'].search([('id','=',vals['analytic_account_id'])], limit=1)
                AccountAnalytics.append(AccountAnalytic.id)
    
        except:
            pass

        if len(AccountAnalytics) <= 0:
            for AccountAnalytic in self.analytic_account_id:
                AccountAnalytic = self.env['account.analytic.account'].search([('id','=',AccountAnalytic.id)])
                
                AccountAnalytics.append(AccountAnalytic.id)

       
        try:
            if  vals['product_id'] is not None:
                _logger.info(" *** product value changed.....")

                product_account = self.env['product.product'].search([('id','=',vals['product_id'])], limit=1)
                budget = self.env['budget.planning'].search([('analytic_account_id','=',AccountAnalytics[0])], limit=1)
                to_budget = self.env['budget.budget'].search([('name','=',budget.name)], limit=1)
                for x in to_budget.budget_line:
                    for bline in x.general_budget_id.account_ids:
                        if product_account.property_account_expense_id.id == bline.id:
                            reserved_amounts.append(x.reserved_amount)
                        budget_codes.append(bline.id)
                product_account_code.append(product_account.property_account_expense_id.id)
            
        except: 
            pass

        if len(product_account_code) <= 0:
            _logger.info("not product value changed.....")
            for pro in self.product_id:
                product_account = self.env['product.product'].search([('id','=',pro.id)], limit=1)
            budget = self.env['budget.planning'].search([('analytic_account_id','=',AccountAnalytics[0])], limit=1)
            to_budget = self.env['budget.budget'].search([('name','=',budget.name)], limit=1)
            for x in to_budget.budget_line:
                    for bline in x.general_budget_id.account_ids:
                        if product_account.property_account_expense_id.id == bline.id:
                            reserved_amounts.append(x.reserved_amount)
                        budget_codes.append(bline.id)
            product_account_code.append(product_account.property_account_expense_id.id)
    
        fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)
        search_mapping = self.env['hr.mapping.employee.account'].search([('employee_id','=',employee_id.id),('accountAnalytic','=',AccountAnalytics[0])], limit=1)
        
        # try:
        total_request = []
        if AccountAnalytic.budget_analytic_account == True:
            # try:
                if search_mapping:
                    # if AccountAnalytic.is_allowed == True:
                   
                    try:
                        if vals['unit_amount'] is not None and vals['quantity']is not None:
                            total_request = float(vals['unit_amount']) * float(vals['quantity'])
                            total_request.append(total_request)
                        elif vals['unit_amount'] is not None and vals['quantity']is None:
                            total_request = float(vals['unit_amount']) * float(self.quantity)
                            total_request.append(total_request)
                        elif vals['unit_amount'] is  None and vals['quantity']is not None:
                            total_request = float(self.unit_amount) * float(vals['quantity'])
                            total_request.append(total_request)
                        elif vals['unit_amount'] is  None and vals['quantity']is  None:
                            total_request = float(self.unit_amount) * float(self.quantity)
                            total_request.append(total_request)
                        else:
                            pass
                    except:
                        pass

                    if product_account_code[0] in budget_codes:
                        reserved_amounts = reserved_amounts[0] 
                        if  search_mapping.is_allowed == True: #AccountAnalytic.department_id == employee_id.department_id and
                            _logger.info("$$$$$$")

                        else:
                            raise UserError(_('This account has not been approved, and the budget approval process has not been completed.'))
                    else:
                        raise UserError(_('The Expense Account are not in this budget code...\n Please ckeck your product Expense Account'))
                else:
                    raise UserError(_('You are not authorized to use this budget account.'))

                    

            # except Exception as e:
            #     _logger.warning("Cannot duplicate!", exc_info=True)
            #     raise ValidationError(e)
        else:
            pass
        # except:
        #     pass
            
        return super(HrExpense, self).write(vals)
    
class CustomExpense(models.Model):
    _inherit = 'hr.expense.sheet'

    def action_sheet_move_create(self):
        res = super(CustomExpense, self).action_sheet_move_create()
        for sheet in self:
            journal = self.env['account.move'].search([('id','=',sheet.account_move_id.id)], limit=1)
            journal.write({'state': 'draft'})
        return res