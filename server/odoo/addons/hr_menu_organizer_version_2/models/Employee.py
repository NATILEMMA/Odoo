"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError  

class Employee(models.Model):
    _inherit = 'hr.employee'

    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user,hr.group_user_custom", copy=False)
    image_128 = fields.Image("Image 128")
    work_email = fields.Char('Work email')
    work_phone = fields.Char('Work Phone')
    job_title = fields.Char("Job Title")
    hr_presence_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('to_define', 'To Define')], default='to_define')