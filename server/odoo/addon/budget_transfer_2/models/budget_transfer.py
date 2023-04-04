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



BudgeType = [
    ('monthly','Monthly'),
    ('quarterly','Quarterly'),
    ('semi','Semi'),
    ('annual','Annual'),


]

STATES_TRANSFER = [
    ('draft', 'Draft'),
    ('requested', 'Requested'),
    ('approved', 'Approved'),
    ('canceled', 'Cancel')
]

class AccountAccount(models.Model):
    _inherit = "account.account"

    is_transfer_account = fields.Boolean("Transfer Account", default=False)


class BudgetTransfer(models.Model):
    _name = "budget.transfer"
    # _inherits = 'account.move'
    _description = 'Budget Transfer'

    name = fields.Char()
    budget_line = fields.One2many('budget.transfer.line', 'budget_id', string='Budget Lines', default={})
    date = fields.Date(required=True)
    journal_id = fields.Many2one('account.journal',required=True)
    time_frame = fields.Many2one('reconciliation.time.fream')
    fiscal_year = fields.Many2one('fiscal.year')
    state = fields.Selection(STATES_TRANSFER,
                              'Status', required=True,
                              copy=False, default='draft',tracking=True)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    prepare_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    prepare_signed_by =  fields.Many2one('hr.employee','Signed By', help='Name of the person that signed the SO.', copy=False)
    prepare_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)

    approver_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    approver_signed_by = fields.Many2one('hr.employee','Signed By', help='Name of the person that signed the SO.', copy=False)
    approver_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    squ = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    def action_transfer_cancel(self):
        self.state = 'canceled'
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        moves.unlink()
        return super(BudgetTransfer, self).write({'state':'canceled'}) 
    

    def action_reset(self):
        self.state = "draft"
        super(BudgetTransfer, self).write({'state':'draft'}) 
    def action_request(self):
        self.state = "requested"
        super(BudgetTransfer, self).write({'state':'requested'}) 
    def action_approve(self):
        account = self.env["account.move"].sudo().create({
            "name": self.squ,
            "ref": self.squ,
            "date": self.date,
            "journal_id": self.journal_id.id,
            "time_frame": self.time_frame.id,
            "fiscal_year": self.fiscal_year.id
        
        })
        _logger.info("account:%s",account)
        lines = []
        

        for index, line in enumerate(self.budget_line):
            vals = []
            val = {}
            val[index] = {}
            val1 = {}
            val3 = {}
            from_budget = self.env['budget.budget'].search([('id','=',line.from_budget_code.id)], limit=1)
            _logger.info("From Budgte %s",from_budget)
            _logger.info("From Budgte %s",from_budget.budget_line.general_budget_id)
            vv = from_budget.budget_line.search([('id','=',line.from_budgetary.id)])
            _logger.info("CCCCCCCCCCCCC line_value_1 %s",from_budget.budget_line)
            _logger.info("CCCCCCCCCCCCC line_value_1 %s",vv.general_budget_id.name)


            from_budget_account = []
            to_budget_account = []
            for line_value_1 in from_budget.budget_line.general_budget_id:
            # line_value_1 = from_budget.budget_line.general_budget_id.search([('id','=',line.from_budgetary.id)])
                _logger.info("BBBBBBBBB line_value_1 %s",line_value_1.name)
                _logger.info("BBBBBBBBB line_value_1 %s",line_value_1.id)
                _logger.info("CCCCCCCCCCCCC line_value_1 %s",line.from_budgetary.id)
                
                _logger.info("BBBBBBBBB line_value_1 %s",line_value_1.account_ids)

                if line.from_budgetary.general_budget_id.id == line_value_1.id:
                
                    _logger.info("YYYYYYYYYYYYYYYYY")
                    
                    # for x in from_budget.budget_line:
                    values = []
                    for bline in line_value_1.account_ids:
                        _logger.info("CCCCCCCC line_value_1 %s",bline.name)
                        _logger.info("CCCCCCCC line_value_1 %s",line.account_from.name)

                        # if line.from_budgetary.id == line_value_1.id:
                        post_value = line_value_1.account_ids.search([('id','=',line.account_from.id)], limit=1)
                        if line.account_from.id == bline.id:
                            pass
                        else:
                            aa = self.env['account.account'].search([('id','=',line.account_from.id)], limit=1)
                            v = {}
                            v['account-ids'] = aa.id
                            k=0
                            # values.append((0,0,bline.id))
                            for k in range(2):
                                if k == 0:
                                    values.append(aa.id)
                                if k == 1:
                                    values.append(bline.id)

                                k = k +1
                            _logger.info("###########  createB ######## %s,%s",line_value_1.account_ids,values)
                            line_value_1.account_ids = [(6,0,values)]
                            # updated = budgetary_line.write(values)
                        # else:
                        #     pass
                        from_budget_account.append(line_value_1.budget_line.analytic_account_id.id)
                        _logger.info("DDDDDDDDDDDDDD from_budget_account %s",from_budget_account)
                        
                       
                else:
                    _logger.info("NNNNNNNNNNNNNN")
            filtered_from_budget_account = res = [*set(from_budget_account)]
            _logger.info("DDDDDDDDDDDDDD filtered_from_budget_account %s",filtered_from_budget_account)

            to_budget = self.env['budget.budget'].search([('id','=',line.to_budget_code.id)], limit=1)
            # for x in to_budget.budget_line:
            values = []
            for line_value_2 in to_budget.budget_line.general_budget_id:
                if line.to_budgetary.general_budget_id.id == line_value_2.id:

                    # line_value_2 = to_budget.budget_line.general_budget_id.search([('id','=',line.to_budgetary.id)])
                    for bline in line_value_2.account_ids:
                                _logger.info("FFFFFFFFF line_value_1 %s",bline.name)
                                _logger.info("FFFFFFFFFFFF line_value_1 %s",line.account_to.name)

                                # if line.from_budgetary.id == line_value_1.id:
                                post_value = line_value_1.account_ids.search([('id','=',line.account_to.id)], limit=1)
                                if line.account_from.id == bline.id:
                                    pass
                                else:
                                    aa = self.env['account.account'].search([('id','=',line.account_to.id)], limit=1)
                                    v = {}
                                    v['account-ids'] = aa.id
                                    k=0
                                    # values.append((0,0,bline.id))
                                    for k in range(2):
                                        if k == 0:
                                            values.append(aa.id)
                                        if k == 1:
                                            values.append(bline.id)

                                        k = k +1
                                    _logger.info("###########  createDD ######## %s,%s",line_value_2.account_ids,values)
                                    line_value_2.account_ids = [(6,0,values)]
                else:
                    pass
                to_budget_account.append(line_value_2.budget_line.analytic_account_id.id)
                _logger.info("to_budget_account %s",to_budget_account)
                filtered_to_budget_account = res = [*set(to_budget_account)]
                _logger.info("filtered_to_budget_account %s",filtered_to_budget_account)


            amount_check = []
            for x in from_budget.budget_line:
                get_code = self.env['account.budget.post'].search([('id','=',x.general_budget_id.id)])
                for v in get_code.account_ids:
                    if line.account_from.id == v.id:
                        amount_check.append(x.reserved_amount)
            _logger.info("######### %s",line.from_budgetary.reserved_amount)
            if line.approved_amount > 0:

                if line.approved_amount <= line.from_budgetary.reserved_amount:
                
                    # if index == 0:
                    i = 0
                    for i in range(2):
                        if i == 0:
                            val1['move_id'] = account.id
                            val1['account_id'] = line.account_from.id
                            val1['analytic_account_id'] = filtered_from_budget_account[0]
                            val1['debit']= float(line.approved_amount)
                            val1['credit']= 0.00
                            lines.append(val1)
                        else:
                            val3['move_id'] = account.id
                            val3['account_id'] = line.account_to.id
                            val3['analytic_account_id'] = filtered_to_budget_account[0]
                            val3['debit']= 0.00
                            val3['credit']= float(line.approved_amount)
                            lines.append(val3)
                        i = i+1
                        _logger.info("LINES: %s",lines)
                    lines = self.env['account.move.line'].sudo().create(lines)
                    # self.move_id = lines.id
                    _logger.info("linse indexs %s, %s", index, lines)
                    lines = []
                    
                    # if index == 1:
                    #     i = 0
                    #     for i in range(2):
                    #         if i == 0:
                    #             val2['move_id'] = account.id
                    #             val2['account_id'] = line.account_from.id
                    #             val2['analytic_account_id'] = from_budget_account[0]
                    #             val2['debit']= float(line.approved_amount)
                    #             val2['credit']= 0.00
                    #             lines.append(val2)
                    #         else:
                    #             val3['move_id'] = account.id
                    #             val3['account_id'] = line.account_to.id
                    #             val3['analytic_account_id'] = to_budget_account[0]
                    #             val3['debit']= 0.00
                    #             val3['credit']= float(line.approved_amount)
                    #             lines.append(val3)
                    #         i = i+1
                    #     _logger.info("Val:%s",lines)
                    #     lines = self.env['account.move.line'].sudo().create(lines)
                    #     _logger.info("linse indexs %s, %s", index, lines)

                    self.move_id = account.id

                else:
                    raise ValidationError("The approved amount is greater than the budget code amount. Please check your approved amount;  it must be less than the transfer budget code amount.")
            else:
                    raise ValidationError("The approved amount fields are required for budget transfer approval.")
           
                
           
        account.action_post()           
        self.state = "approved"
        super(BudgetTransfer, self).write({'state':'approved'}) 

    @api.model
    def create(self, vals):
        if vals.get('squ', _('New')) == _('New'):
            vals['squ'] = self.env['ir.sequence'].next_by_code('budget.transfer') or _('New')
            date = vals['date']
            try:
                date = date.split('-')
                vals['squ'] = "BT/"+date[0]+"/"+vals['squ']
                _logger.info("After :%s",vals['squ'])
                vals['name'] = vals['squ']
            except:
                raise ValidationError("Duplication is not Allowed.")
        res = super(BudgetTransfer, self).create(vals)
        return res
    
class BudgetTransferLine(models.Model):
    _name = "budget.transfer.line"
    _description = 'Budget Transfer Line'

    account_from = fields.Many2one('account.account', 'Account code' ,required=True, domain=[('is_transfer_account', '=', True)])
    account_to = fields.Many2one('account.account', 'Account code',required=True, domain=[('is_transfer_account', '=', True)])
    budget_type = fields.Many2one('budget.type')
    from_budget_code = fields.Many2one('budget.budget', string="From Budget")
    to_budget_code = fields.Many2one('budget.budget', string="To Budget")
    from_budgetary = fields.Many2one('budget.lines', string="Budgetary",domain="[('budget_id', '=', from_budget_code)]")
    to_budgetary = fields.Many2one('budget.lines', string="Budgetary",domain="[('budget_id', '=', to_budget_code)]")
    span = fields.Char(string="   ")
    transfer_amount = fields.Float('Transfer Amount')
    approved_amount = fields.Float('Approved Amount' ,required=True)
    date = fields.Datetime()
    budget_id = fields.Many2one('budget.transfer', string='Releation', index=True,  ondelete='cascade')

    