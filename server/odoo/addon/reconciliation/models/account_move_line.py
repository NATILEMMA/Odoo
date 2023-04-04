# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True,)
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame', domain= "[('fiscal_year', '=', fiscal_year)]", required=True,)

    @api.model
    def create(self, vals):
        print("vals", vals)
        try:
              if vals['time_frame']:
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
            active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
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

        self._recompute_dynamic_lines(recompute_tax_base_amount=True)
        self._move_autocomplete_invoice_lines_values()
        payments = self.env['account.payment'].search([('sale_id', '=', self.ref)])
        print("payments", payments)
        for payment in payments:
            print("payment.sales_type", payment, payment.amount, payment.sales_type)
            self.sales_type = payment.sales_type
        #moves = self.env['account.move'].search([])
        #for move in moves:
            #if move.state == 'posted':
                #for line in move.line_ids:
                    #line.partner_id = move.partner_id.id
        return

    @api.model
    def default_get(self, fields):
        date = self.date
        if not date:
            date = datetime.now()
        # print('date2', date)
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', date),('date_to', '>=', date)],limit=1)
        if not active_time_frame.id and not self.time_frame:
            raise ValidationError(_(
                'please set Time frame for the journal'))
        active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if not active_fiscal_year.id and not self.fiscal_year:
            raise ValidationError(_(
                'please set Active fiscal year for the journal'))
        if not self.time_frame:
          self.time_frame = active_time_frame.id
        if not active_fiscal_year:
          self.fiscal_year = active_fiscal_year.id
        return super(AccountMove, self).default_get(fields)


    @api.onchange('time_frame')
    def onchange_time_frame(self):
          if self.time_frame:
            if not (self.time_frame.date_from <= self.date and self.time_frame.date_to >= self.date):
                raise AccessError(_("You Date is not in this time frame."))
            for line in self.line_ids:
                   line.time_frame = self.time_frame
          if self.fiscal_year:
              for line in self.line_ids:
                  line.fiscal_year = self.fiscal_year

    @api.onchange('date')
    def onchange_date_field(self):
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', self.date), ('date_to', '>=', self.date)], limit=1)
        if not active_time_frame.id:
            raise ValidationError(_(
                'please set Time frame for the journal'))
        else:
            self.time_frame = active_time_frame


    def post(self):
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
    def default_get(self, fields):
        if self.fiscal_year and self.time_frame:
            date = self.date
            if not date:
                date = datetime.now()
            active_time_frame = self.env['reconciliation.time.fream'].search(
                [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
            if not active_time_frame.id and not self.time_frame:
                raise ValidationError(_(
                    'please set Time frame for the journal line'))
            active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)

            if not active_fiscal_year.id and not self.fiscal_year:
                raise ValidationError(_(
                    'please set Active fiscal year for the journal'))
            if not self.time_frame:
             self.time_frame = active_time_frame.id
            if not self.fiscal_year:
             self.fiscal_year = active_fiscal_year.id
        return super(AccountMoveLine, self).default_get(fields)