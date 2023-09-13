from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, ValidationError

import logging


class ReconciliationTimeFream(models.Model):
    _name = "reconciliation.time.fream"
    _description = "time frame for reconciliation"

    name = fields.Char('Description', size=256, required=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    is_active = fields.Boolean('Is Active time frame')
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True)
    time_frame = fields.Many2one('reconciliation.time.fream', 'Time frame')


    @api.model
    def create(self, vals):
       try:
            print("vals.get('date_to') < vals.get('date_from')", vals.get('date_to') , vals.get('date_from'))
            if vals.get('date_to') < vals.get('date_from'):
                raise ValidationError(_(
                    'start date should be less than end date !'))
            domain = [
                ('date_from', '<=',  vals.get('date_to')),
                ('date_to', '>=', vals.get('date_from')),
                ('id', '!=', vals.get('id')),
            ]
            nframe = self.search_count(domain)
            if nframe:
                raise ValidationError(_(
                    'You can not have 2 Time frame that overlaps on same day!'))
            if not vals.get('date_to') and not vals.get('date_from'):
                raise ValidationError(_(
                    'You can not have 2 Time frame that overlaps on same day!'))
            res = super(ReconciliationTimeFream, self).create(vals)
            return res
       except:
           raise ValidationError(_(
               'Please select Date for the Time Frame which dose not overlaps'))
           return

    @api.onchange('name', 'fiscal_year')
    def onchange_name_field(self):
        if self.name and self.fiscal_year:
            name = self.name.split('/')
            self.name = name[0] +"/"+str(self.fiscal_year.name)

