import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import except_orm
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class SalaryAdvanceConf(models.Model):
    _name = "salary.advance.conf"

    percent = fields.Float(string='Maximum allowed', required=True)


    @api.model
    def create(self, vals):
        avr = self.env['salary.advance.conf'].search([])
        if avr:
            raise ValidationError(_('You can not create two salary rule'))
        res_id = super(SalaryAdvanceConf, self).create(vals)
        return res_id