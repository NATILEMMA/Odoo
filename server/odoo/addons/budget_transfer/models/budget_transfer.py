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


class BudgetTransfer(models.Model):
    _name = "budget.transfer"
    # _inherits = 'account.move'
    _description = 'Budget Transfer'

    name = fields.Char(translate=True)
    budget_line = fields.One2many('budget.transfer.line', 'budget_id', string='Budget Lines', default={})
    date = fields.Date()
    journal_id = fields.Many2one('account.journal')
    time_frame = fields.Many2one('reconciliation.time.fream')
    fiscal_year = fields.Many2one('fiscal.year')
    state = fields.Selection(STATES_TRANSFER,
                              'Status', required=True,
                              copy=False, default='draft',tracking=True)
    prepare_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    prepare_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False, translate=True)
    prepare_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)

    approver_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    approver_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False, translate=True)
    approver_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    squ = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), translate=True)

   
    def action_request(self):
        self.state = "requested"
        super(BudgetTransfer, self).write({'state':'requested'}) 
    def action_approve(self):
        account = self.env["account.move"].sudo().create({
            "name": self.squ,
            "ref": self.name,
            "date": self.date,
            "journal_id": self.journal_id.id,
            "time_frame": self.time_frame.id,
            "fiscal_year": self.fiscal_year.id
        
        })
        _logger.info("account:%s",account)
        lines = []
        for line in self.budget_line:
            vals = []
            val = {}
            val1 = {}

            from_budget = self.env['budget.budget'].search([('id','=',line.from_budget_code.id)], limit=1)
            from_budget_account = []
            to_budget_account = []

            for x in from_budget.budget_line:
                from_budget_account.append(x[0].analytic_account_id.id)
            to_budget = self.env['budget.budget'].search([('id','=',line.to_budget_code.id)], limit=1)
            for x in to_budget.budget_line:
                to_budget_account.append(x[0].analytic_account_id.id)
            _logger.info("from_budget_account %s",from_budget_account)
            _logger.info("to_budget_account %s",to_budget_account)

            _logger.info("From Budget Lines %s",from_budget.budget_line)
            amount_check = []
            for x in from_budget.budget_line:
                get_code = self.env['account.budget.post'].search([('id','=',x.general_budget_id.id)])
                for v in get_code.account_ids:
                    if line.account_from.id == v.id:
                        amount_check.append(x.reserved_amount)
            if line.approved_amount > 0:
            
                if line.approved_amount <= amount_check[0]:
                    i = 0
                    for i in range(2):
                        if i == 0:
                            val['move_id'] = account.id
                            val['account_id'] = line.account_from.id
                            val['analytic_account_id'] = from_budget_account[0]
                            val['debit']= float(line.approved_amount)
                            val['credit']= 0.00
                            lines.append(val)
                        else:
                            val1['move_id'] = account.id
                            val1['account_id'] = line.account_to.id
                            val1['analytic_account_id'] = to_budget_account[0]
                            val1['debit']= 0.00
                            val1['credit']= float(line.approved_amount)
                            lines.append(val1)
                        i = i+1
                    lines = self.env['account.move.line'].sudo().create(lines)
                    lines = []
                
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
            try:
                date = date.split('-')
                vals['squ'] = "BT/"+date[0]+"/"+vals['squ']
                _logger.info("After :%s",vals['squ'])
                vals['name'] = vals['squ']
            except:
                raise ValidationError("Duplicate is not Allowed.")
        res = super(BudgetTransfer, self).create(vals)
        return res
    
class BudgetTransferLine(models.Model):
    _name = "budget.transfer.line"
    _description = 'Budget Transfer Line'

    account_from = fields.Many2one('account.account', 'Account' ,required=True)
    account_to = fields.Many2one('account.account', 'Account',required=True)
    budget_type = fields.Many2one('budget.type')
    from_budget_code = fields.Many2one('budget.budget', string="From Budget")
    to_budget_code = fields.Many2one('budget.budget', string="To Budget")
    transfer_amount = fields.Float('Transfer Amount')
    approved_amount = fields.Float('Approved Amount' ,required=True)
    date = fields.Datetime()
    budget_id = fields.Many2one('budget.transfer', string='Releation', index=True,  ondelete='cascade')

    