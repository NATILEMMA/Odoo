# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime
import random
import string
import werkzeug.urls
from odoo import tools
from collections import defaultdict
from datetime import datetime, date
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging

_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []


class AccountMove(models.Model):
    _inherit = "account.move"

    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):

            if i == (len(pick1) - 1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'], pick1[i]['month'], pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year, date1.month, date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) == str:
                        vals['ethiopian_from'] = None
                        vals['date'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) == date:
                        vals['date'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()
        try:
            if vals['date'] is not None:
                date1 = vals['date']
                date_time_obj = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                             int(date_time_obj[2]))
                if type(Edate1) == date:
                    vals['ethiopian_from'] = Edate1
                elif type(Edate1) == str:
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False

                else:
                    pass
        except:
            pass
        try:
            if vals['time_frame']:
                try:
                    if vals['fiscal_year']:
                        return super(AccountMove, self).create(vals)
                    else:
                        id = vals['time_frame']
                        fy = self.env['reconciliation.time.fream'].search(['id', '=', id])
                        vals['fiscal_year'] = fy.fiscal_year.id
                except:
                    return super(AccountMove, self).create(vals)

        except:
            print("except")
            date = self.date
            if not date:
                date = datetime.now()
            # print('date2', date)
            active_time_frame = self.env['reconciliation.time.fream'].search(
                [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
            if not active_time_frame.id:
                raise ValidationError(_(
                    'please set Time frame for the journal'))
            active_fiscal_year = active_time_frame.fiscal_year
            vals['time_frame'] = active_time_frame.id
            vals['fiscal_year'] = active_fiscal_year.id
            print("expect vals", vals)
            return super(AccountMove, self).create(vals)

    def compute_tax(self):
        if self.is_invoice(include_receipts=True):
            company_currency = self.company_id.currency_id
            has_foreign_currency = self.currency_id and self.currency_id != company_currency

            for line in self._get_lines_onchange_currency():
                new_currency = has_foreign_currency and self.currency_id
                line.currency_id = new_currency
                line._onchange_currency()
        else:
            self.line_ids._onchange_currency()

        # self._recompute_dynamic_lines(recompute_tax_base_amount=True)
        # self._move_autocomplete_invoice_lines_values()
        # payments = self.env['account.payment'].search([('sale_id', '=', self.ref)])
        # print("payments", payments)
        # for payment in payments:
        #     print("payment.sales_type", payment, payment.amount, payment.sales_type)
        #     self.sales_type = payment.sales_type
        # moves = self.env['account.move'].search([])
        # for move in moves:
        # if move.state == 'posted':
        # for line in move.line_ids:
        # line.partner_id = move.partner_id.id
        return

    @api.model
    def default_get(self, fields):
        date = self.date
        if not date:
            date = datetime.now()
        # print('date2', date)
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
        if not active_time_frame.id and not self.time_frame:
            raise ValidationError(_(
                'please set Time frame for the journal'))
        # active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        # if not active_fiscal_year.id and not self.fiscal_year:
        #     raise ValidationError(_(
        #         'please set Active fiscal year for the journal'))
        if not self.time_frame:
            self.time_frame = active_time_frame.id
            self.fiscal_year = self.time_frame.fiscal_year.id
        return super(AccountMove, self).default_get(fields)

    @api.onchange('time_frame')
    def onchange_time_frame(self):
        if self.time_frame:
            if not (self.time_frame.date_from <= self.date and self.time_frame.date_to >= self.date):
                raise AccessError(_("You Date is not in this time frame."))
            self.fiscal_year = self.time_frame.fiscal_year.id
            for line in self.line_ids:
                line.time_frame = self.time_frame
                line.fiscal_year = self.time_frame.fiscal_year.id

    @api.onchange('date')
    def onchange_date_field(self):
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', self.date), ('date_to', '>=', self.date)], limit=1)
        if not active_time_frame.id:
            raise ValidationError(_(
                'please set Time frame for the journal'))
        else:
            self.time_frame = active_time_frame
            self.fiscal_year = active_time_frame.fiscal_year.id

    def post(self):
        print("account post")
        print(self.purchase_id,"purchase produt", self.purchase_id.product_id.name,"standard price", self.purchase_id.product_id.standard_price)
        for rec in self:
            flag = self.env['res.users'].has_group('account.group_account_manager')
            if not flag:
                if rec.fiscal_year.state != 'active':
                    raise AccessError(_("You Posting date out of the active fiscal year."))
            active_time_frame = self.env['reconciliation.time.fream'].search(
                [('is_active', '=', True)])
            active = 0
            for line in active_time_frame:
                if rec.date:
                    if line.date_from <= rec.date and line.date_to >= rec.date:
                        active = active + 1
            if active == 0:
                if rec.date:
                    raise AccessError(_("You Posting date out of the current time frame."))
            for line in rec.line_ids:
                line.fiscal_year = rec.fiscal_year.id
                line.time_frame = rec.time_frame.id
            return super(AccountMove, rec).post()

    def write(self, vals):
        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                              int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
                vals['date'] = date_gr
                if type(Edate1) == str:
                    vals['ethiopian_from'] = None
                    vals['pagum_from'] = Edate1
                    vals['is_pagum_from'] = False
                if type(Edate1) == date:
                    vals['ethiopian_from'] = Edate1
                    vals['pagum_from'] = None
                    vals['is_pagum_from'] = True

        except:
            pass
        try:
            if vals['date'] is not None:
                date_str = vals['date']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]), int(date_time_obj[1]),
                                                            int(date_time_obj[2]))
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
        return super(AccountMove, self).write(vals)

    @api.model
    def initial_date(self, data):
        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year, date.month, date.day)

            return date
        else:

            models = mm[0]
            search = self.env[models].search([('id', '=', id[0])])
            if search.ethiopian_from != False and search.pagum_from == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': search.ethiopian_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from != False:
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2] + '-' + date_from_str[0] + '-' + date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': date_from, 'to': today}
            elif search.ethiopian_from == False and search.pagum_from == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
                return {'from': today, 'to': today}
            else:
                date = datetime.now()
                date = EthiopianDateConverter.to_ethiopian(date.year, date.month, date.day)

                return date

    @api.model
    def date_convert_and_set(self, picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date, time = str(datetime.now()).split(" ")
        dd, mm, yy = picked_date['day'], picked_date['month'], picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year, date_gr.month, date_gr.day)
        date = {"data": f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}", "date": date}
        data = {
            'day': picked_date['day'],
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


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_statement_id = fields.Many2one('bank.reconciliation', 'Bank Statement', copy=False)
    statement_date = fields.Date('Bank.St Date', copy=False)
    reconciled = fields.Boolean('Is reconciled')
    is_reconciled = fields.Boolean('Is reconciled')
    is_done = fields.Boolean('Is done')
    time_frame = fields.Many2one('reconciliation.time.fream', 'Time frame', required=True)
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True)

    # def write(self, vals):
    #     if not vals.get("statement_date"):
    #         vals.update({"reconciled": False})
    #         for record in self:
    #             if record.payment_id and record.payment_id.state == 'reconciled':
    #                 record.payment_id.state = 'posted'
    #     elif vals.get("statement_date"):
    #         vals.update({"reconciled": True})
    #         for record in self:
    #             if record.payment_id:
    #                 record.payment_id.state = 'reconciled'
    #     res = super(AccountMoveLine, self).write(vals)

    #     return res

    @api.model
    def create(self, vals):
        id = vals['move_id']
        move_id = self.env['account.move'].search([('id', '=', id)])
        vals['time_frame'] = move_id.time_frame.id
        vals['fiscal_year'] = move_id.fiscal_year.id
        print("account line val ", vals)
        return super(AccountMoveLine, self).create(vals)

    @api.model
    def default_get(self, fields):
        print("default_get")
        self.time_frame = self.move_id.time_frame.id
        print("this is move",self.move_id,"stock move id",self.move_id. stock_move_id,"product name",self.move_id.stock_move_id.product_id.name,"standard price by stock move ",self.move_id.stock_move_id.product_id.standard_price,"product name",self.move_id.stock_move_id.product_id.name,"standard price by product ",self.product_id.standard_price)
        self.fiscal_year = self.move_id.fiscal_year.id
        # if self.fiscal_year and self.time_frame:
        #     date = self.date
        #     if not date:
        #         date = datetime.now()
        #     active_time_frame = self.env['reconciliation.time.fream'].search(
        #         [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
        #     if not active_time_frame.id and not self.time_frame:
        #         raise ValidationError(_(
        #             'please set Time frame for the journal line'))
        #     active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        #
        #     if not active_fiscal_year.id and not self.fiscal_year:
        #         raise ValidationError(_(
        #             'please set Active fiscal year for the journal'))
        #     if not self.time_frame:
        #      self.time_frame = active_time_frame.id
        #     if not self.fiscal_year:
        #      self.fiscal_year = active_fiscal_year.id
        return super(AccountMoveLine, self).default_get(fields)
