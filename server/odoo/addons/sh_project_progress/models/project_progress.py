# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
# For project stage customization
class ProjectStage(models.Model):
    _inherit = 'project.task.type'
    
    stage_progress = fields.Float('Progress(%)')
    exclude = fields.Boolean('Exclude From Progress Calculation',default=False)
    
    @api.constrains('stage_progress')
    def _check_task_progress(self):
        if self.stage_progress > 100 :
            raise ValidationError(_('Progress must be 100% OR under 100%.'))
        
# For project progress         
class ProjectsProgress(models.Model):
    _inherit = 'project.project'
    
    progress = fields.Float('Progress(%)', compute='compute_progressbar')
    total = fields.Integer(compute="compute_progressbar")

    expectation_progress = fields.Float('Progress(%)', compute='expectation_compute_progressbar')
    expectation_total = fields.Integer(compute="expectation_compute_progressbar")
    
    @api.depends('tasks')
    def compute_progressbar(self):
        for rec in self:
            sum = 0.0
            rec.total = 100
            total_task = 0
            rec.progress = 0

            _logger.info("DDDDDDDDDD %s ",rec.tasks)
            for task in rec.tasks:

                _logger.info("DDDDDDDDDD %s ",task.stage_id.stage_progress)
                # _logger.info("DDDDDDDDDD %s ",task.stage_id.stage_progress)
                _logger.info("DDDDDDDDDD %s ",task.kanban_state)

                # if task.stage_id.exclude == False:
                #     sum  += task.stage_id.stage_progress
                #     total_task += 1
                #     rec.progress = sum / total_task
                total_task += 1
                if task.kanban_state == 'done':
                    sum  += task.stage_id.stage_progress
            _logger.info("TTTTTTTTTT sum %s",sum)
            
            _logger.info("TTTTTTTTTT total %s",total_task)
            if sum <= 0:
                rec.progress = 0.0
            else:
                rec.progress = sum / total_task


    @api.depends('tasks')
    def expectation_compute_progressbar(self):
        for rec in self:
            sum = 0.0
            rec.expectation_total = 100
            total_task = 0
            rec.expectation_progress = 0
            total_value = 0.0
            total_quarters = 0.0
            for loop in rec.milestone_ids:
                total_value += loop.progress
                total_quarters +=1

            for task in rec.tasks:
                if task.stage_id.exclude == False:
                    sum  += task.stage_id.stage_progress
                    total_task += 1
                    if total_quarters <= 0:
                        rec.expectation_progress = sum / total_task
                        rec.expectation_total = rec.expectation_total
                    else:
                        rec.expectation_progress = total_value / total_quarters
                        rec.expectation_total = rec.expectation_total


                    
#For Task Progress     
class TaskProgress(models.Model):
    _inherit = 'project.task'            
     
    task_progress = fields.Float('Progress(%)',compute="compute_task_progressbar")
    task_total = fields.Integer('Task total',compute="compute_task_progressbar")     
    
    @api.depends('stage_id')
    def compute_task_progressbar(self):
        for task in self:
            # if task.check_box == False:
            #     task.task_total = 100
            #     task.task_progress = task.stage_id.stage_progress
            # else:
            task.task_total = 100
            task.task_progress = task.progress_rate
        
           