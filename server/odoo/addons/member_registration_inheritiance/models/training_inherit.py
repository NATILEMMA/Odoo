"""This file will deal with training for leaders"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Trainings(models.Model):
    _inherit="leaders.trainings"

    leader_responsibility = fields.Many2one(related="partner_id.leader_responsibility")
