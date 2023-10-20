"""This file will compute the wage of different job titles"""

from odoo import models, api, _


class Transfer(models.Model):
    _inherit = 'transfer.request'
    
    @api.model
    def initial_date(self, data):
        return data
    
class LeaveReport(models.Model):
    _inherit = 'hr.leave.report'
    
    @api.model
    def initial_date(self, data):
        return data
    
class Lawsuit(models.Model):
    _inherit = 'hr.lawsuit'
    
    @api.model
    def initial_date(self, data):
        return data
    
class RequestPosition(models.Model):
    _inherit = 'hr.employee.position.request'
    
    @api.model
    def initial_date(self, data):
        return data

class Complaint(models.Model):
    _inherit = 'employee.complaint'
    
    @api.model
    def initial_date(self, data):
        return data

class Loan(models.Model):
    _inherit = 'hr.loan'
    
    @api.model
    def initial_date(self, data):
        return data
    
class Attendance(models.Model):
    _inherit = 'hr.attendance'
    
    @api.model
    def initial_date(self, data):
        return data

    

  





