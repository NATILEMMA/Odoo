"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError  

class Employee(models.Model):
    _inherit = 'hr.employee'

    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user,hr.group_user_custom", copy=False, translate=True)
    image_128 = fields.Image("Image 128")
    work_email = fields.Char('Work email', translate=True)
    work_phone = fields.Char('Work Phone', translate=True)
    job_title = fields.Char("Job Title", translate=True)
    hr_presence_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('to_define', 'To Define')], default='to_define')
    

    @api.onchange('work_phone')
    def _work_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.work_phone:
                for st in record.work_phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.work_phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.work_phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))
                
    @api.onchange('mobile_phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.mobile_phone:
                for st in record.mobile_phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.mobile_phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.mobile_phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))

    
    @api.onchange('work_email')
    def _validate_email_address(self):
        """This function will validate the email given"""
        for record in self:
            no = ['@', '.']
            if record.work_email:
                if '@' not in record.work_email or '.' not in record.work_email:
                    raise UserError(_("A Valid Email Address has '@' and '.'"))
                        