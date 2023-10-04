from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError


class TenderLimit(models.Model):
    _name = 'tender.limit'
    _description = 'Tender Limit'

    max_amount = fields.Float("Maximum vendor Limit")
    max_amount_2 = fields.Float("Minimum vendor Limit")
    limit_by = fields.Selection(string='Tender Type',
                                selection=[('limit', 'Limited Tender'),
                                           ('open Tender', 'open Tender')])
    fianicial_amount = fields.Float("Financial percentage")
    techinical_amount = fields.Float("Technical percentage")

    @api.model
    def create(self, vals):
        if (vals['fianicial_amount'] + vals['techinical_amount']) != 100:
            raise ValidationError(_("you the sum of Financial rule and technical rule must be 100"))
        if vals['max_amount'] == 0  and vals['limit_by'] == 'limit':
            raise ValidationError(_("Maximum vendor limit can not be zero"))
        if vals['max_amount_2'] == 0 and vals['limit_by'] == 'open Tender':
            raise ValidationError(_("Minimum vendor limit can not be zero"))
        return super(TenderLimit, self).create(vals)

    def write(self, vals):
        res = super(TenderLimit, self).write(vals)
        if (self.fianicial_amount + self.techinical_amount) != 100:
            raise ValidationError(_("you the sum of Financial rule and technical rule must be 100"))
        if self.max_amount  == 0  and self.limit_by  == 'limit':
            raise ValidationError(_("Maximum vendor limit can not be zero"))
        if self.max_amount_2 == 0 and self.limit_by == 'open Tender':
            raise ValidationError(_("Minimum vendor limit can not be zero"))

        return res