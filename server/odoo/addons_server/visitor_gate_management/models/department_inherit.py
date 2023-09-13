# This file will inehrit and add department field


from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta



class Department(models.Model):
    _inherit = "hr.department"


    secretary_ids = fields.Many2many('hr.employee', domain="[('user_id', '!=', False), ('department_id', '=', id)]", required=True)