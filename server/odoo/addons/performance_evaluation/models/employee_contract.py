"""This will handle contract probation period checking"""
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import date


class Contract(models.Model):
    _inherit = 'hr.contract'


    def probation_evaluation_reminder(self):
        """This function will remind manager before probation period"""
        days = 0
        period = self.env['performance.period'].sudo().search([])
        if period:
            days = period.evaluate_before
        else:
            days = 0
        future = date.today() + relativedelta(days=days)
        contracts = self.env['hr.contract'].search([('trial_date_end', '=', future)])
        for contract in contracts:
            model = self.env['ir.model'].search([('model', '=', 'hr.contract'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Probation Evaluation')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': "Probation Period Evaluation",
                'summary': "Evaluation",
                'date_deadline': date.today() + relativedelta(days=days + 14),
                'user_id': contract.employee_id.parent_id.user_id.id,
                'res_model_id': model.id,
                'res_id': contract.id,
                'activity_type_id': activity_type.id
            })
            message = "The End of trial period for your employee " + str(contract.employee_id.name) + " is on " + str(future) + ". Please provide Performance Evaluation for your employee."
            contract.employee_id.parent_id.user_id.notify_warning(message, '<h4>Probation Period Evaluation</h4>', True)