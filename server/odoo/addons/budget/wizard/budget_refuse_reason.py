# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class BudgetRefuseWizard(models.TransientModel):
    """This wizard can be launched from an he.expense (an expense line)
    or from an hr.expense.sheet (En expense report)
    'hr_expense_refuse_model' must be passed in the context to differentiate
    the right model to use.
    """

    _name = "budget.refuse.wizard"
    _description = "Budget Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    budget_ids = fields.Many2many('budget.planning')

    @api.model
    def default_get(self, fields):
        res = super(BudgetRefuseWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        refuse_model = 'budget.planning'
        _logger.info("############ %s",active_ids)
        _logger.info("#######BB##### %s",refuse_model)

        if refuse_model == 'budget.planning':
            res.update({
                'budget_ids': active_ids,
            })
    
        return res

    def budget_refuse_reason(self):
        self.ensure_one()
        _logger.info("#####################")
        _logger.info("##################### %s",self.reason)
        _logger.info("##################### %s",self.budget_ids)

        if self.budget_ids:
            self.budget_ids.refuse_budget(self.reason)

        return {'type': 'ir.actions.act_window_close'}
