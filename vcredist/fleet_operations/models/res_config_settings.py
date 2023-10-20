# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api,fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_per_hour = fields.Float(string='Payment Per Hour', default=320)
    # income_account_id = fields.Many2one("account.account",
    #                                     string="Default Income Account", domain=[('user_type_id', '=', 'Income')],
    #                                     help="Account used for bank deposit")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            payment_per_hour = float(self.env['ir.config_parameter'].sudo().get_param('fleet_operations.payment_per_hour'))
            ,)
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field2 = self.payment_per_hour 
        param.set_param('fleet_operations.payment_per_hour', float(field2))                                                                                                                                                                                                                                            