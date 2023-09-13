"""This file will deal with training for leaders"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class TrainingType(models.Model):
    _name="training.type"
    _description="This will create the training types"

    name = fields.Char(required=True, translate=True, size=64)

    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each Training Type should be Unique')
                        ]


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if int(st) in no:
                        raise UserError(_("You Can't Have A Digit in Training Type"))
