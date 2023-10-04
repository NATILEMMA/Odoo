# Copyright 2009-2019 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unicodedata

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizAccountAssetReport(models.TransientModel):
    _name = "wiz.account.asset.removal.report"
    _description = "Financial Assets report"

    asset_group_id = fields.Many2one(
        comodel_name="account.asset.group",
        string="Asset Group",
        default=lambda self: self._default_asset_group_id(),
    )
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    draft = fields.Boolean(string="Include draft assets")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self._default_company_id(),
    )

   
   
    @api.model
    def _default_asset_group_id(self):
        return (
            self.env["account.asset.group"]
            .search([("parent_id", "=", False)], limit=1)
            .id
        )

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    @api.onchange("company_id")
    def _onchange_company_id(self):
        fy_dates = self.company_id.compute_fiscalyear_dates(fields.date.today())
        self.date_from = fy_dates["date_from"]
        self.date_to = fy_dates["date_to"]

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for wiz in self:
            if wiz.date_to <= wiz.date_from:
                raise UserError(_("The Start Date must precede the Ending Date."))

    def xls_export_removal(self):

        data = self.env['account.asset'].search_read([('date_start','>=',  self.date_from),('date_start','<=',self.date_to),('state','=','removed')],['profile_name','name','estimated_value','sold_price','date_remove','partner_name'])  
        
        print("data of the assets",data)
        datas = {'data':data , "date_from":self.date_from,'date_to': self.date_to}
        
        return self.env.ref('account_asset_management.asset_removal_report').report_action(self, data=datas)
        
        
