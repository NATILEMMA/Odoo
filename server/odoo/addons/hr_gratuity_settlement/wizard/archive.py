"""This file will deal with the archiving members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
import base64


class ArchiveMembers(models.TransientModel):
    _name="analytic.account.wizard"
    _description="This model will handle the analytic count adding"

    gratuity_id = fields.Many2one('hr.gratuity')
    analytic_id = fields.Many2one('account.analytic.account')


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['analytic.account.wizard'].search([('id', '=', self.id)])
        gratuity_id = self.env['product.product'].search([('name', '=', 'Gratuity'), ('default_code', '=', 'GRTEXP_101')])
        if self.analytic_id:
            wizard.gratuity_id.write({
                'analytic_id': self.analytic_id.id
            })
            if wizard.gratuity_id.corrected_employee_gratuity_amount != 0.00:
                expense = self.env['hr.expense'].sudo().create({
                    'name': wizard.gratuity_id.employee_id.name + "'s Gratituty Expense",
                    'product_id': gratuity_id.id,
                    'unit_amount': wizard.gratuity_id.corrected_employee_gratuity_amount,
                    'quantity': 1,
                    'date': date.today(),
                    'employee_id': wizard.gratuity_id.employee_id.id,
                    'gratuity_id': wizard.gratuity_id.id,
                    'analytic_account_id': self.analytic_id.id
                })
                wizard.gratuity_id.write({
                    'state': 'expensed',
                    'expense_id': expense.id
                })
            else:
                expense = self.env['hr.expense'].sudo().create({
                    'name': wizard.gratuity_id.employee_id.name + "'s Gratituty Expense",
                    'product_id': gratuity_id.id,
                    'unit_amount': wizard.gratuity_id.employee_gratuity_amount,
                    'quantity': 1,
                    'date': date.today(),
                    'employee_id': wizard.gratuity_id.employee_id.id,
                    'gratuity_id': wizard.gratuity_id.id,
                    'analytic_account_id': self.analytic_id.id
                })
                wizard.gratuity_id.write({
                    'state': 'expensed',
                    'expense_id': expense.id
                })
        else:
            UserError(_("Please Fill The Required Field"))

    def action_cancel(self):
        """This function will cancel archive"""
        return True
        # member = self.env['res.partner'].browse(self.env.context.get('active_ids'))     
        # member.write({'active': True})
        # if member.user_name:
        #     user = self.env['res.users'].search([('partner_id', '=', member.id)])
        #     user.write({'active': True})