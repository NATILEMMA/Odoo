from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, ValidationError

import logging


class ReconciliationTimeFream(models.Model):
    _name = "fiscal.year"
    _description = "fiscal year"

    name = fields.Char('Description', size=256, requried=True)
    date_from = fields.Date('Date From', requried=True)
    date_to = fields.Date('Date To', requried=True)
    fiscal_year = fields.Many2one('fiscal.year', string="Last Fiscal year")
    close = fields.Many2one('account.move', string="close Entry", ondelete='restrict', copy=False, readonly=True)
    open = fields.Many2one('account.move', string="opening Entry", ondelete='restrict', copy=False, readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('active', 'Active'),
        ('locked', 'Locked'),
        ('closed', 'Closed')], default='draft', string="Status")


    def activate(self):
        if self.date_from or self.date_to:
            raise ValidationError(_('Please select a date'))
        if self.date_from >= self.date_to:
            raise ValidationError(_('End date must be greater then start date'))
        years = self.env['fiscal.year'].search([])
        for year in years:
            if year.state == 'active':
                raise ValidationError(_('There active fiscal year'))
        self.state = 'active'

    def lock(self):
        self.state = 'locked'

    def close(self):
        self.state = 'closed'

    def set_new(self):
        self.state = 'draft'

    def button_open_fiscal(self):
        print(self.date_from, self.date_to)
        if not self.date_from or  not self.date_to:
            raise ValidationError(_('Please select a date'))
        if self.date_from >= self.date_to:
            raise ValidationError(_('End date must be greater then start date'))
        years = self.env['fiscal.year'].search([])
        for year in years:
            if year.state == 'active':
                raise ValidationError(_('There active fiscal year'))
        return {
            'name': 'object',
            'res_model': 'financial.opening',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'nodestroy': True,
            'target': 'current',

        }

    def button_close_fiscal(self):
        return {
            'name': 'object',
            'res_model': 'financial.closing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'nodestroy': True,
            'target': 'current',

        }
