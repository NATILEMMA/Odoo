import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import except_orm
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class LoanConf(models.Model):
    _name = "loan.advance.conf"

    percent = fields.Float(string='amount loan in terms of monthly income', required=True)


    @api.model
    def create(self, vals):
        avr = self.env['loan.advance.conf'].search([])
        if avr:
            raise ValidationError(_('You can not create two company loan rule'))
        res_id = super(LoanConf, self).create(vals)
        return res_id