"""This file will deal with the candidate members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ethiopian_date import EthiopianDateConverter

class CandidateMembers(models.Model):
    _inherit="candidate.members"


    work_experience_ids = fields.One2many('work.experience', 'candidate_id')
    educational_history = fields.One2many('education.history', 'candidate_id')
    archive_ids = fields.One2many('archived.information', 'candidate_id')