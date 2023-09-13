import datetime
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import json
import logging
_logger=logging.getLogger(__name__)

date_format = "%Y-%m-%d"




class HrSalarySummary(models.Model):
    _inherit = 'salary.summary'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), translate=True)
