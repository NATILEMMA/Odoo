"""This file will deal with the handling of supporter members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import http




class SupportingMembers(models.Model):
    _inherit="supporter.members"


    educational_history = fields.One2many('education.history', 'supporter_id')
    archive_ids = fields.One2many('archived.information', 'supporter_id')
    donation_ids = fields.One2many('donation.payment', 'supporter_id', domain="[('year', '=', year_of_payment)]")