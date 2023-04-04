from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _compute_accounts(self):
        for rec in self:
            if rec.account_move:
                rec.account_move = rec.account_move
            else:

                moves = self.env['account.move'].search(
                    ['|', ('account_payment', '=', rec.id), ('account_payment', '=', rec.id)]).ids
                for move in self.env['account.move'].browse(moves):
                    rec.account_move = move.id

    def _debit_account(self):
        for rec in self:
            self._credit_account()
            if rec.journal_id.type != 'sale':
                rec.debit_account = rec.journal_id.default_debit_account_id.id

                sales_journal = self.env['account.journal'].search(
                    [('company_id', '=', rec.company_id.id), ('type', '=', 'sale')], order='id desc', limit=1)
                if sales_journal:
                    rec.journal_id = sales_journal.id
            else:

                rec.debit_account = self.bank_no

    @api.depends('sales_type')
    def _credit_account(self):
        for rec in self:
            if rec.sales_type == 'advance':
                lines = self.env['saorder_le.order.line'].search([('order_id', '=', rec.sale_id.id)]).ids

                for order_line in self.env['sale.order.line'].browse(order_lines):
                    rec.credit_account = order_line.product_id.advance_account.id
            else:

                rec.credit_account = rec.credit_account

    bank_no = fields.Many2one("account.account",
                              string="bank Account")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 readonly=True, states={'draft': [('readonly', False)]}, tracking=True,
                                 domain="[('company_id', '=', company_id)]", store=True)

    sales_type = fields.Selection(
        [('cash', 'Cash'),
         ('advance', 'Advance'),
         ('full_credit', 'Full Credit'),
         ('advance_credit', 'Advance Credit'), ('last_year_collection', 'Last Year Collection(Not Invoiced)')

         ], string="Sales Type")
    debit_account = fields.Many2one("account.account",
                                    string="Debit Account")
    credit_account = fields.Many2one("account.account",
                                     string="Credit Account")
    income_account_id = fields.Many2one("account.account",
                                        string="Income Account", domain=[('user_type_id', '=', 'Income')],
                                        help="Account used for bank deposit")
    bank_account_id = fields.Many2one("account.account",
                                      string="Bank Account")
    liablity_account_id = fields.Many2one("account.account",
                                          string="Advance Account", domain=[('user_type_id', '=', 'Payable')],
                                          help="Account used for bank deposit")
    sale_id = fields.Many2one('sale.order', "Sale", readonly=True,
                              states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirm'),
        ('validated', 'Validated'),
        ('posted', 'Posted'),
        ('last_year', 'Last Year Sales'),
        ('sent', 'Sent'), ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled')], default='draft', string="Status")
    transaction_ref = fields.Char("Transaction Ref.")
    write_off_balance = fields.Float("write_off_balance")
    withholding_amount = fields.Float("Withholding Amount")
    taxed_amount = fields.Float(string="Vat Amount")
    untaxed_amount = fields.Float("untaxed_amount")
    invoice_ref = fields.Char("Invoice Ref.")

    withholding_account = fields.Many2one("account.account",
                                          string="Withholding Account")
    taxed_account = fields.Many2one("account.account", string="Vat Account")
    account_move = fields.Many2one('account.move', string='Account Move', compute="_compute_accounts"
                                   )
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]")
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True, copy=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    qty_to_invoice = fields.Float(string='To Invoice Quantity', store=True, readonly=True,
                                  digits='Product Unit of Measure')
    is_change = fields.Boolean(string="Is Change", default=False)
    payment_type = fields.Char("Payment type")
    is_last_payment = fields.Boolean(string="Is Change", default=False)
    advance_tax_line_ids = fields.One2many('advanced.tax', 'sale_id', string='Taxes', store=True)

    # @api.onchange('debit_account', 'credit_account','bank_no')
    @api.depends('bank_no')
    def _compute_main(self):
        self._debit_account()
        self._debit_account()
        for rec in self:

            if rec.bank_no and rec.invoice_ref and rec.sales_type and rec.state == 'draft':
                rec.state = 'confirm'

            else:
                rec.state = rec.state

    @api.onchange('amount_advance')
    def onchange_amount(self):
        self.currency_amount = self.amount_advance * (1.0 / self.exchange_rate)
        if self.amount_total != self.amount_advance:
            self.is_last_payment = False
        elif self.amount_total == self.amount_advance:
            if self.invoice_type == "cash_advance":
                self.payment_type = "Advance payment"
                self.is_last_payment = False
            else:
                self.is_last_payment = True

    def validate(self):
        """Create customer paylines and validates the payment"""
        print("validate")
        sale = self.env['sale.order'].browse(self.sale_id.id)
        sales_lines = self.env['sale.order.line'].search([('order_id', '=', sale.id)]).ids
        # for sales_line in self.env['sale.order.line'].browse(sales_lines):
        # print("sales_line", sales_line)
        # self.env.cr.execute(
        #     """SELECT account_tax_id as account_tax_id FROM
        #     account_tax_sale_order_line_rel  WHERE  sale_order_line_id = %d""" % (sales_line.id)
        # )
        # query_result = self.env.cr.dictfetchall()
        # tax_lines = []
        # for val in query_result:
        #     tax_id = val['account_tax_id']
        #     print("tax_id", tax_id)
        #     tax_accounts = self.env['account.tax'].search([('id', '=', tax_id)]).ids
        #     for tax_account in self.env['account.tax'].browse(tax_accounts):
        #         if self.sales_type != 'cash':
        #             # print("under if")
        #             # vat = tax_account.amount * self.amount / 100
        #         else:
        #             print("under else")
        #             vat = tax_account.amount * sale.amount_untaxed/ 100
        #         print("vat", vat)
        #         tax_account_repartition = self.env['account.tax.repartition.line'].search(
        #             [('invoice_tax_id', '=', tax_id), ('repartition_type', '=', 'tax')],
        #             order='id desc',
        #             limit=1)
        #         print("loop")
        sales_tax = self.env['sale.order.tax'].search([('sale_id', '=', sale.id)])
        tax_lines = []
        if self.sales_type == 'cash':
            print("sales_tax", sales_tax)
            for tax in sales_tax:
                name = tax.name
                print("name", name)
                amount = tax.amount
                account = tax.account_id.id
                tax_id = tax.tax_id

                tax_lines.append((0, 0, {
                    'name': name,
                    'account_id': account,
                    'amount': amount,
                    'tax_id': tax_id.id,
                }))
            if self.advance_tax_line_ids:
                self.advance_tax_line_ids.unlink()
            print("tax_lines", tax_lines)
            self.advance_tax_line_ids = tax_lines
        else:
            for tax in sales_tax:
                acc = self.env['account.tax'].search([('id', '=', tax.tax_id.id)])
                name = tax.name
                print("name", name,"self.amount",self.amount)
                amount = (acc.amount * self.amount) / 100
                account = tax.account_id
                tax_id = tax.tax_id
                tax_lines.append((0, 0, {
                        'name': name,
                        'account_id': account.id,
                        'amount': amount,
                        'tax_id': tax_id.id,
                    }))

            if self.advance_tax_line_ids:
                self.advance_tax_line_ids.unlink()
            self.advance_tax_line_ids = tax_lines

        if self.sale_id:
            payment_obj = self.env['account.payment']
            sale_obj = self.env['sale.order']

            sale_ids = self.sale_id
            if sale_ids:
                sale_id = sale_ids.id
                sale = sale_obj.browse(sale_id)

                partner_id = sale.partner_id.id

                date = self.payment_date
                company = sale.company_id

                # To calculate tax amount of paid amount
                amount_tax = self.env['sale.order'].search([('id', '=', sale_id)]).amount_tax
                amount_total = self.env['sale.order'].search([('id', '=', sale_id)]).amount_total
                tax_advance_amount = self.amount * amount_tax / amount_total

                # to find tax amount

                sale_ids = self.env['sale.order.line'].search([('order_id', '=', sale_id)]).ids
                self.write({
                    "is_change": True,
                    "state": "validated",

                })
                for sale in self.env['sale.order.line'].browse(sale_ids):
                    values = {}
                    values['product_id'] = sale.product_id
                    values['product_uom'] = sale.product_uom
                    values['qty_to_invoice'] = sale.qty_to_invoice
                    values['tax_ids'] = sale.tax_id
                    values['analytic_tag_ids'] = sale.order_id.analytic_account_id.id
                    values['analytic_account_id'] = sale.analytic_tag_ids.ids
                    self.write({
                        "product_id": values['product_id'],
                        "product_uom": values['product_uom'],
                        "qty_to_invoice": values['qty_to_invoice'],
                        "tax_ids": values['tax_ids'],
                        "analytic_tag_ids": values['analytic_tag_ids'],
                        "analytic_account_id": values['analytic_account_id']})

        else:
            self.write({"state": "validated"})

    def posted(self):
        print("self.sales_type", self.sales_type)
        if self.sale_id:
            print("self.sales_type", self.sales_type)
            if self.sales_type == 'cash':
                print("if self.sales_type=='cash':")
                all_move_vals = []
                move_vals = {
                    'date': self.payment_date,
                    'type': 'out_invoice',
                    'ref': self.communication,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.journal_id.currency_id.id or self.company_id.currency_id.id,
                    'partner_id': self.partner_id.id,
                    'state': 'draft',

                    'line_ids': [
                        # bank account /debit account
                        (0, 0, {
                            'name': self.debit_account.name,
                            'debit': self.sale_id.amount_total,
                            'credit': 0.0,
                            'account_id': self.debit_account.id,
                            'payment_id': self.id,
                            'exclude_from_invoice_tab': True,

                        }),

                    ],
                }
                line_id = self.sale_id.id
                line = self.env['sale.order.line'].search([('order_id', '=', line_id),('product_uom_qty', '>', 0.0)]).ids

                for order_line in self.env['sale.order.line'].browse(line):

                    acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                              ]).property_account_income_id
                    print("product account", acc)
                    raise Warning(_("Income account product is empty" + str(order_line.product_id.id)))
                    if not acc:
                        if order_line.product_id.name:
                            raise ValidationError(_("Income account product " + order_line.product_id.name + " is empty"))
                        else:
                            raise ValidationError(
                                _("Income account product is empty"))
                    else:
                        move_vals['line_ids'].append(

                            (0, 0, {
                                'name': order_line.product_id.name,
                                'debit': 0.0,
                                'credit': order_line.price_unit * order_line.product_uom_qty,
                                'account_id': (self.env['product.product'].search([('id', '=', order_line.product_id.id
                                                                                    )]).property_account_income_id).id,
                                'payment_id': self.id,
                                'exclude_from_invoice_tab': False,
                                'product_id': order_line.product_id.id,
                                'price_unit': order_line.price_unit,
                                'product_uom_id': order_line.product_uom.id,
                                'quantity': order_line.product_uom_qty,
                                'tax_ids': [(6, 0, order_line.tax_id.ids)],
                            })
                        )
                all_move_vals.append(move_vals)
                print("advance",move_vals)
                # return all_move_vals
                self.env['account.move'].sudo().create(move_vals)
                self.state = 'posted'
                print('posted')
            else:

                all_move_vals = []
                move_vals = {
                    'date': self.payment_date,
                    'type': 'out_invoice',
                    'ref': self.communication,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.journal_id.currency_id.id or self.company_id.currency_id.id,
                    'partner_id': self.partner_id.id,
                    'state': 'draft',

                    'line_ids': [
                        # bank account /debit account
                        (0, 0, {
                            'name': self.debit_account.name,
                            'debit': self.amount,
                            'credit': 0.0,
                            'account_id': self.debit_account.id,
                            'payment_id': self.id,
                            'exclude_from_invoice_tab': True,

                        }),

                    ],
                }
                line_id = self.sale_id.id
                line = self.env['sale.order.line'].search([('order_id', '=', line_id)]).ids
                for order_line in self.env['sale.order.line'].browse(line):
                    acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                              ]).property_account_income_id
                    move_vals['line_ids'].append(

                        (0, 0, {
                            'name': self.debit_account.name,
                            'debit': 0.0,
                            'credit': self.amount - self.taxed_amount,
                            'account_id': self.credit_account.id,
                            'payment_id': self.id,
                            'exclude_from_invoice_tab': False,
                            'tax_ids': [(6, 0, order_line.tax_id.ids)],
                        })

                    )

                all_move_vals.append(move_vals)
                self.env['account.move'].sudo().create(move_vals)
                self.state = 'posted'
                # return all_move_vals

        else:
            super(AccountPayment, self)._prepare_payment_moves()

    def confirm(self):
        self.state = 'confirm'
        self.validate()


@api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'payment_type', 'write_off_balance')
def _compute_payment_difference(self):
    if self.write_off_balance:
        self.payment_difference = self.write_off_balance
        self.payment_difference_handling = 'reconcile'
    else:
        super(AccountPayment, self)._compute_payment_difference()


@api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
def _compute_destination_account_id(self):
    if self.partner_type == 'customer':
        self.payment_difference = self.write_off_balance
        self.payment_difference_handling = 'reconcile'
        if self.liablity_account_id:
            self.destination_account_id = self.liablity_account_id.id
        else:
            self.destination_account_id = self.income_account_id.id
    else:
        super(AccountPayment, self)._compute_destination_account_id()


class AdvanceedTax(models.Model):
    _name = "advanced.tax"
    _description = "Advanced Tax"

    name = fields.Char("Tax name")
    sale_id = fields.Many2one('account.payment', string='Sale', ondelete='cascade', index=True)
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    account_id = fields.Many2one('account.account', string='Tax Account', domain=[('deprecated', '=', False)])
    amount = fields.Float()


class AccountMove(models.Model):
    _inherit = "account.move"

    def compute_tax(self):
        self._move_autocomplete_invoice_lines_values()
        return

    def action_post(self):
        self._move_autocomplete_invoice_lines_values()
        return super(AccountMove, self).action_post()




