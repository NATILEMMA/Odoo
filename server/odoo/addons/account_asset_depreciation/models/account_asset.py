from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    monthly_depreciation = fields.Monetary(compute='compute_monthly_depreciation')
    peryear_depreciation = fields.Float(compute='compute_peryear_depreciation')
    lst_year_amount = fields.Monetary()
    c_year_amount = fields.Monetary()
    s_period_amount = fields.Monetary()
    s_remaining_value = fields.Monetary()
    s_depreciated_value = fields.Monetary()
    months = fields.Integer(compute='compute_months')
    total_remaining = fields.Monetary()

    def compute_monthly_depreciation(self):
        for record in self:
            depreciation = (record.value - record.salvage_value) / record.months
            record.monthly_depreciation = depreciation

    def compute_months(self):
        months = 0
        for record in self:
            if record.method_time == 'number':
                months = record.method_period * record.method_number
                record.months = months
            else:
                if record.date_first_depreciation == 'manual':
                    months = (record.method_end.year - record.first_depreciation_manual_date.year) * 12 + (record.method_end.month - record.first_depreciation_manual_date.month)
                    record.months = months
                else:
                    months = (record.method_end.year - record.date.year) * 12 + (record.method_end.month - record.date.month)
                    record.months = months

    def compute_peryear_depreciation(self):
        for record in self:
            if record.months >= 12:
                percentage = (record.monthly_depreciation*12)*100
                if record.value > 0:
                    depreciation = percentage/record.value
                else:
                    depreciation = 0
                record.peryear_depreciation = round(depreciation, 2)
            else:
                percentage = (record.monthly_depreciation *
                              record.method_number)*100
                if record.value > 0:
                    depreciation = percentage/record.value
                else:
                    depreciation = 0
                record.peryear_depreciation = round(depreciation, 2)
