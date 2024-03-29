# -*- coding: utf-8 -*-
# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    purchase_id = fields.Many2one('purchase.order', "Purchase")
    credit_account_id = fields.Many2one("account.account", string="Credit Account", store=True)
    debit_account_id = fields.Many2one("account.account", string="Debit Account", store=True)
    effective_date = fields.Date(string="Debit Account")
    bank_reference = fields.Char(string="Bank Reference",translate=True)
    cheque_reference = fields.Char(string="Cheque Reference",translate=True)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False,
                                      readonly=True)
    payment_Type = fields.Selection([
        ('Direct', 'Direct payment'),
        ('employee', 'Payment by employee')],
        string='Payment Type', required=True, default='employee')
    is_advance = fields.Boolean("Is Advance", default= False)

    @api.model
    def create(self, vals):
        print("def create")
        debit_account_id = self.env["res.config.settings"].search([], limit=1, order='id desc').purchase_account
        print(debit_account_id)
        vals.update({'debit_account_id': debit_account_id.id})

        return super(AccountPayment, self).create(vals)

    def post(self):
      if self.partner_type == 'supplier':
            if self.journal_id.default_credit_account_id and self.partner_id.property_account_payable_id:
                self.credit_account_id = self.journal_id.default_credit_account_id.id
                self.debit_account_id = self.partner_id.property_account_payable_id.id
            account_ids = self.env.context.get('active_ids', [])
            if account_ids:
                res_2 = super(AccountPayment, self).post()
                res = self.env['account.move'].search([('id', '=', account_ids[0])])
                acc = self.env['account.move'].search([('ref', '=', res.name)])
                for rec in acc:
                  res.account_move_id =rec.id
                return res_2
            date = self.payment_date
            if not date:
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
            seq = self.env['ir.sequence'].next_by_code('advance.purchase.sequence')
            print("seq", seq)
            if self.payment_Type == 'Direct':
                partner = self.purchase_id.partner_id.id
            else:
                partner = self.purchase_id.user_id.partner_id.id
            move_vals = [(0, 0, {
                'name': self.credit_account_id.name,
                'debit': 0.0,
                'credit': self.amount,
                'account_id': self.credit_account_id.id,
                'payment_id': self.id,
                'exclude_from_invoice_tab': True,
                'partner_id': partner or False,
            }),
                         (0, 0, {
                             'name': self.debit_account_id.name,
                             'debit': self.amount,
                             'credit': 0.0,
                             'account_id': self.debit_account_id.id,
                             'payment_id': self.id,
                             'exclude_from_invoice_tab': False,
                             'partner_id': partner or False,
                         })]

            print("move_vals", move_vals, seq, self.purchase_id.name)
            inv_values = {
                'name': seq,
                'partner_id': partner or False,
                # 'ref': self.purchase_id.name,
                'journal_id': self.journal_id.id,
                'line_ids': move_vals,
                'type': 'entry',
                'date': self.payment_date,
                'purchase_id': self.purchase_id.id,
                'state': 'posted',
                'flag_2': True,
                'fiscal_year': fiscal_year,
                'time_frame': time_frame,
                # 'is_invoice_receive': True,

            }

            move = self.env['account.move'].sudo().create(inv_values)
            self.account_move_id = move.id
            self.state = 'posted'
            return
      else:
          return super(AccountPayment,self).post()



class AccountMove(models.Model):
    _inherit = "account.move"

    flag = fields.Char(string="flag", store=True,translate=True)
    flag_2 = fields.Boolean(string="Is Change", default=False)
    purchase_id = fields.Many2one('purchase.order', "Purchase", store=True)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False,
                                      readonly=True)

    def action_post(self):
        print("action_post")
        word = self.name
        print(word, word[:3])
        self.flag = word[:3]
        if self.flag == 'ADV':
            self.flag_2 = True
            print("self.flag_2", self.flag_2)
        else:
            self.flag_2 = False
            print("self.flag_2", self.flag_2)
        return super(AccountMove, self).action_post()
