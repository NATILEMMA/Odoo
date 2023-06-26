# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date

class AssetDepreciationReportWizard(models.TransientModel):
    _name = "asset.depreciation.report.wizard"
    _description = "Asset depreciation report"

    def all_categories(self):
            return self.env['account.asset.category'].search([]).ids
            
    category = fields.Many2many('account.asset.category', required=True, default=all_categories)
    date_from= fields.Date(string='Date from', required=True)
    date_to= fields.Date (string='Date to', required=True)
    lst_end_year= fields.Date(compute='compute_lst_year')

    


    def compute_lst_year(self):
            for record in self:
                date= record.date_from
                lst_end_year= date.replace(year=record.date_from.year-1, day=31, month=12)
                record.lst_end_year = lst_end_year

    def check_date(self):
        for record in self:
            if  record.date_to.year != record.date_from.year:
                raise UserError('Please select a date in the same fiscal year')

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'category': self.category.ids,
            'lst_end_year': self.lst_end_year,
        },
        }
        return self.env.ref('account_asset_depreciation.depreciation_report').report_action(self, data=data)