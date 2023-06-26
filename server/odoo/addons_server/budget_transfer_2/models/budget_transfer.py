import logging
from datetime import date
from datetime import datetime, timedelta,date
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
from ethiopian_date import EthiopianDateConverter
pick1 = []
pick2 = []
pick3 = []
pick4 = []

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


    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')

    name = fields.Char()
    budget_line = fields.One2many('budget.transfer.line', 'budget_id', string='Budget Lines', default={})
    date = fields.Date()
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
    @api.onchange('date')
    def onchange_date_field(self):
        if not self.date:
           pass
        else:
            _logger.info("bbbbbbbbbbbbbbbb %s",self.date)
            active_time_frame = self.env['reconciliation.time.fream'].search(
                [('date_from', '<=', self.date), ('date_to', '>=', self.date)], limit=1)
            if not active_time_frame.id:
                raise ValidationError(_(
                    'please set Time frame for the journal'))
            else:
                self.time_frame = active_time_frame
                self.fiscal_year = active_time_frame.fiscal_year.id

    def action_transfer_cancel(self):
        self.state = 'canceled'
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        moves.unlink()
        return super(BudgetTransfer, self).write({'state':'canceled'}) 
    
    def unlink(self):
        if self.state in ['requested','approved']:
            state = self.state
            raise ValidationError('You cannot delete a budget transfer request that has been '+self.state)

    def action_reset(self):
        self.state = "draft"
        super(BudgetTransfer, self).write({'state':'draft'}) 
    def action_request(self):
        self.state = "requested"
        super(BudgetTransfer, self).write({'state':'requested'}) 
         
    def action_reject(self):
        self.state = "canceled"
        super(BudgetTransfer, self).write({'state':'canceled'})
        
    def action_approve(self):
        account = self.env["account.move"].sudo().create({
            "name": self.squ,
            "ref": self.squ,
            "date": self.date,
            "journal_id": self.journal_id.id,
            "time_frame": self.time_frame.id,
            "fiscal_year": self.fiscal_year.id,
            "is_budget_transfer_journal": True
        
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
            _logger.info("kkkkkkkkkkkkkkk line_value_1 %s",vv.general_budget_id.is_transfer_code)


            from_budget_line_code = []
            from_budget_account = []
            to_budget_account = []
            to_budget_line_code = []

            if vv.general_budget_id.is_transfer_code == True:
            

                for line_value_1 in from_budget.budget_line.general_budget_id:
                # line_value_1 = from_budget.budget_line.general_budget_id.search([('id','=',line.from_budgetary.id)])
                    _logger.info("BBBBBBBBB line_value_1 %s",line_value_1.name)
                    _logger.info("BBBBBBBBB line_value_1 %s",line_value_1.id)
                    _logger.info("CCCCCCCCCCCCC line_value_1 %s",line.from_budgetary.id)
                    
                    _logger.info("BBBBBBBBB line_value_1 %s",line_value_1.account_ids)

                    if line.from_budgetary.general_budget_id.id == line_value_1.id:
                        
                        _logger.info("YYYYYYYYYYYYYYYYY")
                        from_budget_line_code.append(line.from_budgetary.general_budget_id.id)
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
                            budget = self.env['account.analytic.account'].search([('name','=',from_budget.name)], limit=1)
                            _logger.info("DDDDDDDDDDDDDD %s",budget)
                            from_budget_account.append(budget.id)
                            _logger.info("DDDDDDDDDDDDDD from_budget_account %s",from_budget_account)
                            
                        
                    else:
                        _logger.info("NNNNNNNNNNNNNN")
            else:
                raise ValidationError('You cannot transfer from the budget code '+'"'+ vv.general_budget_id.name + '"' +' because it is a non-transferable budget code.')

            filtered_from_budget_account  = [*set(from_budget_account)]
            _logger.info("DDDDDDDDDDDDDD filtered_from_budget_account %s",filtered_from_budget_account)
            filtered_from_budget_line_code = [*set(from_budget_line_code)]
            to_budget = self.env['budget.budget'].search([('id','=',line.to_budget_code.id)], limit=1)
            # for x in to_budget.budget_line:
            values = []
            for line_value_2 in to_budget.budget_line.general_budget_id:
                if line.to_budgetary.general_budget_id.id == line_value_2.id:
                    to_budget_line_code.append(line.to_budgetary.general_budget_id.id)
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
                budget = self.env['account.analytic.account'].search([('name','=',to_budget.name)], limit=1)

                to_budget_account.append(budget.id)
                _logger.info("to_budget_account %s",to_budget_account)
                filtered_to_budget_account = [*set(to_budget_account)]
                _logger.info("filtered_to_budget_account %s",filtered_to_budget_account)
                filtered_to_budget_line_code = [*set(to_budget_line_code)]


            amount_check = []
            for x in from_budget.budget_line:
                get_code = self.env['account.budget.post'].search([('id','=',x.general_budget_id.id)])
                for v in get_code.account_ids:
                    if line.account_from.id == v.id:
                        amount_check.append(x.reserved_amount)
            _logger.info("MMMMMMMMMMMMMMMMMMMMMMM %s",filtered_from_budget_line_code)
            _logger.info("MMMMMMMMMMMMMMMMMMMMMMM %s",filtered_to_budget_line_code)


            if line.approved_amount > 0:

                if line.approved_amount <= line.from_budgetary.reserved_amount:
                
                    # if index == 0:
                    i = 0
                    for i in range(2):
                        if i == 0:
                            val1['move_id'] = account.id
                            val1['account_id'] = line.account_from.id
                            val1['analytic_account_id'] = filtered_from_budget_account[0]
                            val1['budget_line_code'] = filtered_from_budget_line_code[0]
                            val1['amount'] = float(-(line.approved_amount))
                            val1['debit']= float(line.approved_amount) 
                            val1['credit']= 0.00
                            val1['time_frame']= self.time_frame.id
                            val1['fiscal_year'] = self.fiscal_year.id
                            lines.append(val1)
                        else:
                            val3['move_id'] = account.id
                            val3['account_id'] = line.account_to.id
                            val3['analytic_account_id'] = filtered_to_budget_account[0]
                            val3['budget_line_code'] = filtered_to_budget_line_code[0]
                            val3['amount'] = float(line.approved_amount)
                            val3['debit']= 0.00
                            val3['credit']= float(line.approved_amount)
                            val3['time_frame']= self.time_frame.id
                            val3['fiscal_year'] = self.fiscal_year.id
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
           
                
           
        # account.action_post()           
        self.state = "approved"
        super(BudgetTransfer, self).write({'state':'approved'}) 

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['date'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()
                vals['squ'] = self.env['ir.sequence'].next_by_code('budget.transfer') or _('New')
                
                date_1 = str(date1)
                date_1 = date_1.split('-')
                vals['squ'] = "BT/"+date_1[0]+"/"+vals['squ']
                _logger.info("After :%s",vals['squ'])
                vals['name'] = vals['squ']
                # The blow code used for only budget transfer moduel

                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', date1), ('date_to', '>=', date1)], limit=1)
                vals['time_frame'] = active_time_frame.id
                vals['fiscal_year'] = active_time_frame.fiscal_year.id


        try:
            if vals['date'] is not None:
                date1 = vals['date']
                date_time_obj = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate1) ==   date:
                    vals['ethiopian_from'] = Edate1
                elif type(Edate1) ==   str :
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False

                else:
                    pass
                vals['squ'] = self.env['ir.sequence'].next_by_code('budget.transfer') or _('New')

                date_1 = str(date1)
                date_1 = date_1.split('-')
                vals['squ'] = "BT/"+date_1[0]+"/"+vals['squ']
                _logger.info("After :%s",vals['squ'])
                vals['name'] = vals['squ']
                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', date1), ('date_to', '>=', date1)], limit=1)
                vals['time_frame'] = active_time_frame.id
                vals['fiscal_year'] = active_time_frame.fiscal_year.id


        except:
            pass

        return super(BudgetTransfer, self).create(vals)
    


    def write(self, vals):
        _logger.info("############# Write:%s",vals)
        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_from'] = Edate1
                        vals['pagum_from'] = None
                        vals['is_pagum_from'] = True

                # The blow code used for only budget transfer moduel

                active_time_frame = self.env['reconciliation.time.fream'].search(
                    [('date_from', '<=', vals['date']), ('date_to', '>=', vals['date'])], limit=1)
                if not active_time_frame.id:
                    pass
                else:
                    self['time_frame'] = active_time_frame
                    self['fiscal_year'] = active_time_frame.fiscal_year.id
        except:
            pass
        try:           
            if vals['date'] is not None:
                date_str = vals['date']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate) == str:
                    vals['ethiopian_from'] = None
                    vals['is_pagum_from'] = False
                    vals['pagum_from'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_from'] = Edate
                    vals['is_pagum_from'] = True
                    vals['pagum_from'] = ' '
        except:
            pass
        return super(BudgetTransfer, self).write(vals)
    
    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            _logger.info("################# not fund")
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            _logger.info("################# d: %s",date)

            return date
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            if search.ethiopian_from != False and search.pagum_from == False:
                _logger.info("################# T")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': search.ethiopian_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from != False:
                _logger.info("#################  T pa")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2]+'-'+ date_from_str[0]+'-'+ date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': date_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from == False:
                _logger.info("#################  F")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': today}
            else:
                date = datetime.now()
                date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
                _logger.info("################# d: %s",date)

                return date

    @api.model
    def date_convert_and_set(self,picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)
        if picked_date['pick'] == 4:
            pick3.append(data)


    
class BudgetTransferLine(models.Model):
    _name = "budget.transfer.line"
    _description = 'Budget Transfer Line'

    account_from = fields.Many2one('account.account', 'Account code' ,required=True, default=lambda self: self.env['account.account'].search([('is_transfer_account','=',True)], limit=1))
    account_to = fields.Many2one('account.account', 'Account code',required=True,  default=lambda self: self.env['account.account'].search([('is_transfer_account','=',True)], limit=1))
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

    