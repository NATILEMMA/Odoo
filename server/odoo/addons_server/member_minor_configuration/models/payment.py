"""This file will deal with the modification of the membership payment"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import os
import re
from odoo.tools import config
import base64
import hashlib
import logging

original = 0.00

_logger = logging.getLogger(__name__)

class PaymentFeeConfiguration(models.Model):
    _name="payment.fee.configuration"
    _description="This model will handle the configuration of payment based on income range"
    _order = "sequence, id"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    minimum_wage = fields.Float(required=True, string="Minimum Wage", track_visibility='onchange')
    maximum_wage = fields.Float(string="Maximum Wage", track_visibility='onchange')
    fee_in_percent = fields.Float(required=True, string="Fee in Percent", track_visibility='onchange')
    sequence = fields.Integer(default=1)

    _sql_constraints = [
                    ('check_on_fee_in_percent', 'CHECK(fee_in_percent <= 100)', 'Fee in Percent Must be Less Than 100')
                    ]


    @api.onchange('maximum_wage')
    def _check_maximum_wage(self):
        """This function will check if maximum wage is correct"""
        for record in self:
            all_fee = self.env['payment.fee.configuration'].search([])
            for fee in all_fee:
                if fee.minimum_wage <= record.maximum_wage <= fee.maximum_wage:
                    raise UserError(_("Configuration for Maximum Wage all ready exists"))



    @api.onchange('minimum_wage')
    def _check_minimum_wage(self):
        """This function will check if maximum wage is correct"""
        for record in self:
            all_fee = self.env['payment.fee.configuration'].search([])
            for fee in all_fee:
                if fee.minimum_wage <= record.minimum_wage <= fee.maximum_wage:
                    raise UserError(_("Configuration for Minimum Wage all ready exists")) 
