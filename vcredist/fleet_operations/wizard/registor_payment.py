# ©  2020 Deltatech
# See README.rst file on addons root folder for license details
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError


class RegistoerPayment(models.TransientModel):
    _name = "register.payment"
    _description = "Register Payment Wizard"

    debit_account = fields.Many2one('account.account', string='Debit Account')
    credit_account = fields.Many2one('account.account', string='Credit Account')
    service = fields.Many2many('fleet.vehicle.log.services', 'services')
    amount = fields.Float(string='amount')
    ref = fields.Char(string='reference')
    date = fields.Date(string='deposit Date')
    journal_id = fields.Many2one('account.journal', 'Journal')

    @api.onchange('service')
    def _service_change(self):
        amount = 0.0
        for ser in self.service:
            if ser.state == 'draft' or ser.state =='approved' or ser.state =='requested' or ser.state == 'register' or ser.state == 'cancel':
                raise ValidationError("You can not registor  "+ ser.name +" it state is  " + str(ser.state))
            print("ser.service_amount", ser.service_amount)
            invoice = 0.0
            for line in ser.service_invoice_id:
               if line.state == 'posted':
                invoice = line.amount_total + invoice
            ser.invoice_amount = invoice
            amount = amount + invoice

        self.amount = amount

    @api.model
    def default_get(self, fields_list):
        res = super(RegistoerPayment, self).default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        print("active_ids", active_ids)
        line_2 = []
        for line in active_ids:
            line_2.append(line)
        res.update({"service": [(6, 0, line_2)]})

        return res
     
    def have_differnce(self):
        for ser in self.service:
            invoice = 0.0
            if ser.service_invoice_id:
                for line in ser.service_invoice_id:
                      if line.state == 'posted':    
                        invoice = line.amount_total + invoice
                ser.invoice_amount = invoice
        return


    def register(self):
        seq = self.env['ir.sequence'].next_by_code('service.register.payment')
        partner_id = self.env.user.partner_id.id
        opreating_unit = self.env.user.default_operating_unit_id.id
        for ser in self.service:
            name = ser.name
        move_vals = [(0, 0, {
            'name': self.credit_account.name,
            'debit': 0.0,
            'credit': self.amount,
            'account_id': self.credit_account.id,
            'exclude_from_invoice_tab': True,
            'date': self.date,
            'operating_unit_id': opreating_unit,
            'partner_id': partner_id or False,
        }),
                     (0, 0, {
                         'name': self.debit_account.name,
                         'debit': self.amount,
                         'date': self.date,
                         'operating_unit_id': opreating_unit,
                         'credit': 0.0,
                         'account_id': self.debit_account.id,
                         'exclude_from_invoice_tab': False,
                         'partner_id': partner_id or False,
                     })]

        inv_values = {
            'name': seq,
            'partner_id': partner_id or False,
            'ref': name,
            'operating_unit_id': opreating_unit,
            'journal_id': self.journal_id.id,
            'line_ids': move_vals,
            'date': self.date,
            'state': 'posted',
            'narration': self.ref,

        }
        print("inv_values", inv_values)
        move = self.env['account.move'].sudo().create(inv_values)
        for serv in self.service:
            serv.state = 'register'
            serv.account_move_id = move.id
        return