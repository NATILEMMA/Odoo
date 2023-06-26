"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class GratuityExpenseGeneration(models.Model):
    _inherit = "hr.gratuity"


    def create_expense(self):
        """This function will create an expense based on gratuity"""
        for record in self:
            wizard = self.env['analytic.account.wizard'].create({
                'gratuity_id': record.id
            })
            return {
                'name': _('Add Analytic Account'),
                'type': 'ir.actions.act_window',
                'res_model': 'analytic.account.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }



class GratuityExpenseInheritance(models.Model):
    _inherit = "hr.expense"

    gratuity_id = fields.Many2one('hr.gratuity', readonly=True, string="Gratuity")