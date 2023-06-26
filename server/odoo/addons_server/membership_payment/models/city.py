from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class CityPayment(models.Model):
    _name = "city.payment"
    _description = "This model will help to handel subcity payment"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Subcity", defualt='draft', readonly= True)
    name_2 = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    amount = fields.Float(string='amount')
    main = fields.Many2one('main.branch', string="Fiscal year")
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    payments = fields.One2many('sub.payment', 'city', string='payments')
    payments_2 = fields.One2many('supporter.payment.sub', 'rev', string='payments')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    amount_4 = fields.Float(string='Supporter/Doner payment')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('register', 'Register'), ], default='draft', string="Status", tracking=True)
    user = fields.Many2one('res.users')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('sub.city.payment')
        vals.update({'name': seq})
        payment = self.env['city.payment'].search(
            [('time_frame', '=', vals['time_frame']), ('name_2', '=', vals['name_2'])])
        for line in payment:
            if line.state == 'draft' or line.state == 'submit':
                raise UserError(_("There is already existing payment that is not closed"))
        return super(CityPayment, self).create(vals)

    @api.onchange('time_frame', 'name_2')
    def _get_lines_2(self):
        if self.time_frame and self.name_2:
            self.payments_2 = [(5, 0, 0)]
            self.payments = [(5, 0, 0)]
            member = self.env['sub.payment'].search(
                [('time_frame', '=', self.time_frame.id), ('name_2', '=', self.name_2.id)])
            val = []
            amount = 0
            for line in member:
               if line.state == 'submit':
                    amount = line.amount_2 + amount
                    val.append(line.id)
            self.user = self.name_2.parent_manager.id
            self.payments = val
            self.amount = amount

        doner_payment = self.env['donation.payment'].search(
            [('month', '=', self.time_frame.id), ('payment_for', '=', 'subcity'), ('subcity_id', '=', self.name_2.id)
                , ('state', '=', 'submit')])
        print("doner_payment", doner_payment)
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
        self.payments_2 = val_2
        self.amount = self.amount_4 + self.amount


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

    def set_submit(self):
        if self.amount_2 == 0:
            raise UserError(_("There is already existing payment that is not closed"))
        for line in self.payments:
            line.state = 'register'
        self.state = 'submit'

    def unlink(self):
         if self.state != 'draft':
              raise UserError(_("You can only draft stage payment"))
         return super(CityPayment,self).unlink()


class SupporterPaymentSub(models.Model):
    _name = 'supporter.payment.sub'

    rev = fields.Many2one("city.payment")
    sup = fields.Many2one("supporter.members", string='members')
    donors = fields.Many2one("donors", string='donors')
    amount = fields.Float("amount")
    type = fields.Selection([
        ('supporter', 'Supporters payment'),
        ('donor', 'Donors payment'), ], default='supporter', string="supporter")

