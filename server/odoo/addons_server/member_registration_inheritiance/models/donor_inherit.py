"""This file will deal with the handling of donors"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class Donors(models.Model):
    _inherit="donors"


    archive_ids = fields.One2many('archived.information', 'donor_id')
    donation_ids = fields.One2many('donation.payment', 'donor_ids', domain="[('year', '=', year_of_payment)]")