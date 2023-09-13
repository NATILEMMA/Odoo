"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _

from odoo.exceptions import UserError  

class Grade(models.Model):
  
  _name="hr.job.grade"
  
  _description="This class will create grades for a job positions"  

  name = fields.Char(required=True, copy=False, string="Grade Name", translate=True)
  job_grade_title = fields.Many2one(related="job_dup_id.name")
  fixed_wage = fields.Float(required=True, copy=False,store=True)
  job_dup_id = fields.Many2one('hr.job.dup')

  @api.onchange('fixed_wage')
  def change_all_employee_with_fixed_wage(self):
    if self.fixed_wage:
      for rec in self:
        contracts = self.env['hr.contract'].search([('job_id','=',rec.job_grade_title.id),('grade_id','=',rec._origin.id)])
        for contract in contracts :
          contract.wage = rec.fixed_wage

class JobDuplicate(models.Model):
  
  _name="hr.job.dup"
  
  _description = "This class will handle the addtion of job grades to their respective job positions"

  name = fields.Many2one('hr.job', required=True)
  
  job_dup_ids = fields.One2many('hr.job.grade', 'job_dup_id' ,required=True)


  @api.onchange('name')
  def _compute_name_repeation(self):
     """This function will check to see if there is repeation in job positions"""
     if self.name:
       all_values = self.env['hr.job.dup'].search([])
       # Find a mapped value of all the job positions with their given ids, hence = mapped('name.id')
       all_job_ids = all_values.mapped('name.id')
       if self.name.id in all_job_ids:
          job_position = self.env['hr.job'].browse(self.name.id)
          message = f"A job position by the name {job_position.name} already exists."
          raise UserError(_(message))


class JobWageCheck(models.Model):
  
  _inherit="hr.contract"

  grade_id = fields.Many2one('hr.job.grade', domain="[('job_grade_title', '=', job_id)]", required=True, string="Grade")


  @api.onchange('grade_id')
  def change_wage_with_grade_with_fixed_wage(self):
    if self.grade_id:
      for rec in self:
        rec.wage = rec.grade_id.fixed_wage