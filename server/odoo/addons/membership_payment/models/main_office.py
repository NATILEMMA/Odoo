from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MainBranch(models.Model):
    _name = "main.branch"
    _description = "This model will help to handel subcity payment"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Subcity", defualt='draft', readonly=True,translate=True)
    amount = fields.Float(string='amount')
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    payments = fields.One2many('city.payment', 'main', string='payments')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('register', 'Register'), ], default='draft', string="Status")
    cash_account_id = fields.Many2one("account.account",
                                      string="Bank Account",  domain=['|',('user_type_id', '=', 'Bank and Cash'),
                                                                      ('user_type_id', '=', 'ባንክ እና ጥሬ ገንዘብ')],
                                      required=True)
    income_account_id = fields.Many2one("account.account",
                                        string="Income Account", domain=['|',('user_type_id', '=', 'Income'),
                                                                            ('user_type_id', '=', 'ገቢ')],
                                        required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, )
    account_move = fields.Many2one('account.move', string='Account Move')
    date = fields.Date("Date", required=True,
                       default=fields.Date.context_today)
    payment_ref = fields.Char("Payment Ref.",translate=True)
    payments_2 = fields.One2many('supporter.payment.main', 'rev', string='supporter/donor payments')
    amount_4 = fields.Float(string='Supporter/Donor payment')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('city.payment')
        vals.update({'name': seq})
        payment = self.env['main.branch'].search(
            [('time_frame', '=', vals['time_frame'])])
        for line in payment:
            if line.state == 'draft' or line.state == 'submit':
                if line.id != self.id:    
                    raise UserError(_("There is already existing payment that is not closed"))
        return super(MainBranch, self).create(vals)

    @api.onchange('time_frame')
    def _get_lines_2(self):
        if self.payments_2:
            self.payments_2 = [(5, 0, 0)]
            self.payments = [(5, 0, 0)]
        payment = self.env['main.branch'].search(
            [('time_frame', '=', self.time_frame.id)])
        for line in payment:
            if line.state == 'draft' or line.state == 'submit':
                raise UserError(_(" There is already existing payment that is not closed."))
        if self.time_frame:
            member = self.env['city.payment'].search([('time_frame', '=', self.time_frame.id)])
            doner_payment = self.env['donation.payment'].search(
                [('month', '=', self.time_frame.id), ('payment_for', '=', 'city'), ('state', '=', 'submit')])
            print("doner_payment", doner_payment)
            val = []
            amount = 0
            for line in member:
                if line.state == 'submit':
                    amount = line.amount_2 + amount
                    val.append(line.id)
            self.payments = val
            self.amount = amount

            val_2 = []
            s_amount = 0
            for line in doner_payment:
                if line.product_cash == 'cash':
                    s_amount = s_amount + line.amount
                    if line.for_donor_or_supporter == "supporter":
                        val_2.append((0, 0, {
                            'sup': line.supporter_id.id,
                            'amount': line.amount,
                            'type': 'supporter'

                        }))
                    else:
                        val_2.append((0, 0, {
                            'donors': line.donor_ids.id,
                            'amount': line.amount,
                            'type': 'donor'
                        }))
            self.amount_4 = s_amount
            self.amount_3 = self.amount_2 - (self.amount_4 + self.amount)
            self.amount = s_amount + self.amount
            self.payments_2 = val_2

    @api.onchange('payments', 'amount_2')
    def _payment_opnchange(self):
        amount = 0
        for line in self.payments:
            amount = line.amount_2 + amount
        self.amount = amount
        self.amount_3 = self.amount_2 - (self.amount_4 + self.amount)
        self.amount = self.amount_4 + self.amount

    def set_draft(self):
        for line in self.payments:
            line.state = 'submit'
        self.state = 'draft'

    def set_post(self):
        move_vals = {
            'date': self.date,
            'invoice_date': self.date,
            'type': 'entry',
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'state': 'draft',
            'fiscal_year': self.fiscal_year.id,
            'time_frame': self.time_frame.id,
            'line_ids': [],

        }
        move_vals['line_ids'].append((0, 0, {
            'name': self.income_account_id.name,
            'debit': 0.0,
            'credit': self.amount_2,
            'account_id': self.income_account_id.id,
            'partner_id': self.env.user.partner_id.id,
            'exclude_from_invoice_tab': False,
        }))

        move_vals['line_ids'].append((0, 0, {
            'name': self.cash_account_id.name,
            'debit': self.amount_2,
            'credit': 0.0,
            'account_id': self.cash_account_id.id,
            'partner_id': self.env.user.partner_id.id,
            'exclude_from_invoice_tab': False,
        }))
        move = self.env['account.move'].sudo().create(move_vals)
        self.account_move = move.id
        self.state = 'register'

    def set_submit(self):
        if self.amount_2 == 0:
            raise UserError(_("you can not submit zero amount received"))
        for line in self.payments:
            line.state = 'register'
        self.state = 'submit'

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_("You can only draft stage payment"))
        return super(MainBranch, self).unlink()


class SupporterPaymentMain(models.Model):
    _name = 'supporter.payment.main'

    rev = fields.Many2one("main.branch")
    sup = fields.Many2one("supporter.members", string='members')
    donors = fields.Many2one("donors", string='donors')
    amount = fields.Float("amount")
    type = fields.Selection([
        ('supporter', 'Supporters payment'),
        ('donor', 'Donors payment'), ], default='supporter', string="supporter")
