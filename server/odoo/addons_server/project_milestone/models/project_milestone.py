
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time
from datetime import timedelta
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)

QUARTERS = [
    ('1st_quarter','1st quarter'),
    ('2nd_quarter','2nd quarter'),
    ('3rd_quarter','3rd quarter'),
    ('4th_quarter','4th quarter'),
    ('Full Year','Full Year'),
]

QUARTERS_T = [
    ('1st quarter','1st quarter'),
    ('2nd quarter','2nd quarter'),
    ('3rd quarter','3rd quarter'),
    ('4th quarter','4th quarter'),
    ('Full Year','Full Year'),
]


class QuartersGoalsTarget(models.Model):
    _name = "planning.goal.target"

    name = fields.Char(string="Target Area", required=True)
   
class QuartersGoals(models.Model):
    _name = "planning.goal"

    name = fields.Char(string="Gaol",required=True)
    quarter_type = fields.Many2one('planning.quarter',string="Quarter", required=True)
    planning_id = fields.Many2one('project.project',string="Planning")
    target_area = fields.Many2one('planning.goal.target',string="Target Area", required=True)
    weight = fields.Float(default="0", multi="progress", store=True)
    start_date = fields.Date(default=datetime.now().date())
    end_date = fields.Date(default=datetime.now().date())
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )

    @api.onchange('quarter_type')
    def _compute_quarters_type(self):
        _logger.info(" Name: %s",self.name)
        if self.quarter_type is not False:
            self.start_date = self.quarter_type.start_date
            self.end_date  = self.quarter_type.end_date
            self.fiscal_year  = self.quarter_type.fiscal_year

        # fiscal_year = self.env['fiscal.year'].search([('state','=','active')], limit=1)
        # self.fiscal_year = fiscal_year.id
        # for rec in self:
        #     today = datetime.now()
        #     year = fiscal_year.ethiopian_to.year
        #     # extract the year from today's date
        #     # year = today.year
        #     start_date = date(year-1, 11, 1)

        #     _logger.info("SSSSSSSSSSSSSSS %s",start_date)
        #     # calculate the end date of each quarter
        #     q1_end = date(year, 1, 30)
        #     q2_end = date(year, 4, 30)
        #     q3_end = date(year, 7, 30)
        #     q4_end = date(year, 10, 30)

        #     # assign the start and end dates to each quarter
        #     q1_start = start_date 
        #     q2_start = q1_end + timedelta(days=2)
        #     q3_start = q2_end + timedelta(days=1)
        #     q4_start = q3_end + timedelta(days=2)
        #     input_qrt = str(self.name).split(' ') 
        #     _logger.info("Input quarters id %s",input_qrt[0][0])
        #     if self.name == False:
        #         pass
        #     else:
        #         value  = int(input_qrt[0][0])
        #         if value == 1:
        #             self.start_date = q1_start
        #             self.end_date  = q1_end
        #         elif value == 2:
        #             self.start_date = q2_start
        #             self.end_date  = q2_end
        #         elif value == 3:
        #             self.start_date = q3_start
        #             self.end_date  = q3_end 
        #         elif value ==4 :
        #             self.start_date = q4_start
        #             self.end_date  = q4_end
        #         else:
        #             pass


            

class Quarters(models.Model):
    _name = "planning.quarter"

    name = fields.Selection(QUARTERS_T, string="Name", translate=True, required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )

   

    @api.onchange('name')
    def _compute_quarters_type(self):
      
        # self.fiscal_year = fiscal_year.id
        try:
            fiscal_year = self.env['fiscal.year'].search([('id','=',self.fiscal_year.id)], limit=1)
            _logger.info("FFFFFFFFFFFFFFFFFFF %s",fiscal_year.name)
            _logger.info(" Quarter Name: %s",self.name)

            for rec in self:
                today = datetime.now()
                year = int(fiscal_year.name)
                # Convert Ethiopian year to Gregorian
                # gregorian_date = EthiopianDateConverter.to_gregorian(int(year),1,1)

                # # Extract the Gregorian year
                # year = gregorian_date.year
                # _logger.info("FFFFFFFFFFFF year FFFFFFF %s",year)

                start_date = date(year-1, 11, 1)
                q1_end = date(year, 1, 30)
                q2_end = date(year, 4, 30)
                q3_end = date(year, 7, 30)
                q4_end = date(year, 10, 30)

                # assign the start and end dates to each quarter
                q1_start = start_date 
                q2_start = q1_end + timedelta(days=2)
                q3_start = q2_end + timedelta(days=1)
                q4_start = q3_end + timedelta(days=2)
                input_qrt = str(self.name).split(' ') 
                _logger.info("Input quarters id %s",input_qrt[0][0])
                if self.name == False:
                    pass
                else:
                    if input_qrt[0][0] == 'F':
                        date1 = str(q1_start)
                        date2 = str(q4_end)
                        date_time_obj = date1.split('-')
                        date_time_obj2 = date2.split('-')
                        date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                        date_gr2 = EthiopianDateConverter.to_gregorian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
               
                        Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                        Edate2 = EthiopianDateConverter.to_ethiopian(date_gr2.year,date_gr2.month,date_gr2.day)
                        if type(Edate1) ==   str:
                                self.ethiopian_from = None
                                self.pagum_from = Edate1
                                self.is_pagum_from = False
                        if type(Edate1) ==   date:
                                self.ethiopian_from = Edate1
                                self.pagum_from = None
                                self.is_pagum_from = True

                        if type(Edate2) ==   str:
                                self.ethiopian_to = None
                                self.pagum_to = Edate2
                                self.is_pagum_to = False
                        if type(Edate2) ==   date:
                                self.ethiopian_to = Edate2
                                self.pagum_to = None
                                self.is_pagum_to = True

                        self.start_date = date_gr
                        self.end_date  = date_gr2
                    else:
                        value  = int(input_qrt[0][0])
                        if value == 1:
                            date1 = str(q1_start)
                            date2 = str(q1_end)
                            date_time_obj = date1.split('-')
                            date_time_obj2 = date2.split('-')
                            date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                            date_gr2 = EthiopianDateConverter.to_gregorian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                
                            Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                            Edate2 = EthiopianDateConverter.to_ethiopian(date_gr2.year,date_gr2.month,date_gr2.day)
                            if type(Edate1) ==   str:
                                    self.ethiopian_from = None
                                    self.pagum_from = Edate1
                                    self.is_pagum_from = False
                            if type(Edate1) ==   date:
                                    self.ethiopian_from = Edate1
                                    self.pagum_from = None
                                    self.is_pagum_from = True

                            if type(Edate2) ==   str:
                                    self.ethiopian_to = None
                                    self.pagum_to = Edate2
                                    self.is_pagum_to = False
                            if type(Edate2) ==   date:
                                    self.ethiopian_to = Edate2
                                    self.pagum_to = None
                                    self.is_pagum_to = True

                            self.start_date = date_gr
                            self.end_date  = date_gr2
                        elif value == 2:
                            # self.start_date = q2_start
                            # self.end_date  = q2_end
                            date1 = str(q2_start)
                            date2 = str(q2_end)
                            date_time_obj = date1.split('-')
                            date_time_obj2 = date2.split('-')
                            date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                            date_gr2 = EthiopianDateConverter.to_gregorian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                
                            Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                            Edate2 = EthiopianDateConverter.to_ethiopian(date_gr2.year,date_gr2.month,date_gr2.day)
                            if type(Edate1) ==   str:
                                    self.ethiopian_from = None
                                    self.pagum_from = Edate1
                                    self.is_pagum_from = False
                            if type(Edate1) ==   date:
                                    self.ethiopian_from = Edate1
                                    self.pagum_from = None
                                    self.is_pagum_from = True

                            if type(Edate2) ==   str:
                                    self.ethiopian_to = None
                                    self.pagum_to = Edate2
                                    self.is_pagum_to = False
                            if type(Edate2) ==   date:
                                    self.ethiopian_to = Edate2
                                    self.pagum_to = None
                                    self.is_pagum_to = True

                            self.start_date = date_gr
                            self.end_date  = date_gr2
                        elif value == 3:
                            # self.start_date = q3_start
                            # self.end_date  = q3_end 
                            date1 = str(q3_start)
                            date2 = str(q3_end)
                            date_time_obj = date1.split('-')
                            date_time_obj2 = date2.split('-')
                            date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                            date_gr2 = EthiopianDateConverter.to_gregorian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                
                            Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                            Edate2 = EthiopianDateConverter.to_ethiopian(date_gr2.year,date_gr2.month,date_gr2.day)
                            if type(Edate1) ==   str:
                                    self.ethiopian_from = None
                                    self.pagum_from = Edate1
                                    self.is_pagum_from = False
                            if type(Edate1) ==   date:
                                    self.ethiopian_from = Edate1
                                    self.pagum_from = None
                                    self.is_pagum_from = True

                            if type(Edate2) ==   str:
                                    self.ethiopian_to = None
                                    self.pagum_to = Edate2
                                    self.is_pagum_to = False
                            if type(Edate2) ==   date:
                                    self.ethiopian_to = Edate2
                                    self.pagum_to = None
                                    self.is_pagum_to = True

                            self.start_date = date_gr
                            self.end_date  = date_gr2
                        elif value ==4 :
                            # self.start_date = q4_start
                            # self.end_date  = q4_end
                            date1 = str(q4_start)
                            date2 = str(q4_end)
                            date_time_obj = date1.split('-')
                            date_time_obj2 = date2.split('-')
                            date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                            date_gr2 = EthiopianDateConverter.to_gregorian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                
                            Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                            Edate2 = EthiopianDateConverter.to_ethiopian(date_gr2.year,date_gr2.month,date_gr2.day)
                            if type(Edate1) ==   str:
                                    self.ethiopian_from = None
                                    self.pagum_from = Edate1
                                    self.is_pagum_from = False
                            if type(Edate1) ==   date:
                                    self.ethiopian_from = Edate1
                                    self.pagum_from = None
                                    self.is_pagum_from = True

                            if type(Edate2) ==   str:
                                    self.ethiopian_to = None
                                    self.pagum_to = Edate2
                                    self.is_pagum_to = False
                            if type(Edate2) ==   date:
                                    self.ethiopian_to = Edate2
                                    self.pagum_to = None
                                    self.is_pagum_to = True

                            self.start_date = date_gr
                            self.end_date  = date_gr2
                        
                        else:
                            pass
        except:
            pass


            

class ProjectMilestone(models.Model):
    _name = "project.milestone"
    # _order = "project_id,sequence"
    _description = "Project Milestone"

    @api.depends("project_task_ids.stage_id", "project_task_ids.stage_id.closed")
    def _get_default_planning_id(self):
        _logger.info("##############_get_default_planning_id###############")
        for rec in self:
            planning_id = self.env['project.project'].search([('name','=', rec.project_id.name)],limit=1)
            if planning_id is not False:
                _logger.info("yyyyyyyyyyyyyyy")
                return planning_id.id
            else:
                _logger.info("NNNNNNNNNNN")

                return False
    # name = fields.Selection(QUARTERS, string="Name", required=True)

    name = fields.Many2one('planning.quarter',string="Quarter", required=True)
    target_date = fields.Date(help="The date when the Quarters should be complete.")
    start_date = fields.Date()
    end_date = fields.Date()
    progress = fields.Float(
        compute="_compute_milestone_progress",
        store=True,
        help="Percentage of Completed Tasks vs Incomplete Tasks.",
    )
    project_id = fields.Many2one("project.project", string="Planning")
    project_task_ids = fields.One2many(
        "project.task", "milestone_id", string="Planning Tasks"
    )
    fold = fields.Boolean(string="Kanban Folded?")
    sequence = fields.Integer()

    @api.model
    def create(self, vals):
        seq = self.env["ir.sequence"].next_by_code("project.milestone") or 0
        vals["sequence"] = seq
        return super().create(vals)
    

    @api.onchange('name')
    def _compute_quarters_type(self):
        _logger.info(" Name: %s",self.name)
        _logger.info(" Name: %s",self.name.start_date)
        

        for rec in self:
            _logger.info(" Name: %s",rec.name)
            # Define the two dates to compare
            if rec.name is not False:
                self.start_date = rec.name.start_date
                self.end_date = rec.name.end_date
           

            

          

    # @api.onchange('name')
    # def _compute_quarters(self):
    #     for rec in self:
    #         planning_id = self.env['project.project'].search([('name','=', rec.project_id.name)],limit=1)
    #         if self.name == False:
    #             pass
    #         else:
    #             for loop in planning_id.milestone_ids:

    #                 if loop.name == self.name:
                        
    #                     raise ValidationError("The "+str(self.name) + " has already been defined in the " +rec.project_id.name)
    #                 else:
    #                     pass
                        
            
    
    # @api.onchange('start_date','end_date')
    # def _compute_start_and_end_date_of_quarters(self):
    #     for rec in self:
    #         active = self.env.context.get('active_id')
    #         active_id = self.env.context.get('active_id')
    #         planning_id = self.env['project.project'].search([('name','=', rec.project_id.name)],limit=1)
    #         planning = rec.project_id
    #         for loop in planning_id.milestone_ids:
    #             loop_qrt = str(loop.name).split('_') 
    #             input_qrt = str(self.name).split('_') 

    #             _logger.info("quarters id %s",loop_qrt[0][0])
    #             _logger.info("Input quarters id %s",input_qrt[0][0])

    #             _logger.info(" start date: %s, input Date: %s",loop.start_date, self.start_date)
    #             # Define the two dates to compare
    #             date1 = datetime.strptime(str(loop.start_date), '%Y-%m-%d')
    #             date2 = datetime.strptime(str(loop.end_date), '%Y-%m-%d')
    #             _logger.info("SSSSSSSS date: %s and EEEEEEEEEEEE date: %s",date1,date2)
    #             # Define the third input date
    #             if loop.name == False:
    #                 pass
    #             elif self.name == False:
    #                 pass
    #             else:
    #                 if int(loop_qrt[0][0]) +1 == int(input_qrt[0][0]):
    #                     _logger.info("YYYYYYYYYYYYYYYYYYYYYY   %s,%s",input_qrt,loop_qrt)
    #                     inputDate = str(self.start_date).split(' ')
    #                     input_date = datetime.strptime(inputDate[0], '%Y-%m-%d')
    #                     # if date2 >= date1:
    #                     #     raise ValidationError("The End date cannot be less than start date.")
    #                     # else:
    #                     if date1 <= input_date <= date2:
    #                         raise ValidationError("The start date cannot be less than the end date of the "+loop.name+".")
    #                     elif input_date <= date1:
    #                         raise ValidationError("The start date cannot be less than the "+loop.name+" start date.")
                    
    #                     else:
    #                         _logger.info('The input date is not between date1 and date2')
    #                 else:
    #                     pass
            
    #             # Compare the input date with the two dates
                
               
    #             # if  loop.start_date > self.start_date:
    #             #     raise ValidationError("The Start date must greater than defined" +loop.name)
    #             # else:
    #             #     pass
    #     pass



    @api.depends("project_task_ids.stage_id", "project_task_ids.stage_id.closed", "project_task_ids.info_checklist.status")
    def _compute_milestone_progress(self):
        for record in self:
            planning_id = self.env['project.project'].search([('name','=', record.project_id.name)],limit=1)
            self.project_id = planning_id.id
            total_task = len(record.project_task_ids)
            total_tasks_count = 0.0
            total_weight = 0.0
            closed_tasks_count = 0.0

            total_value = 0.0
            total_value2 = 0.0
            for task_record in record.project_task_ids:
                total_tasks_count += 1
                _logger.info("kkkkkkkkk %s",task_record.weight)
                _logger.info("kkkkkkkkkVVVV %s",task_record.done_weight)

                total_weight += task_record.weight
                if task_record.check_box == False:
                    total_value2 += task_record.done_weight

                    if task_record.stage_id.name == 'done':
                        closed_tasks_count += 1
                else:
                    total_value2 += task_record.done_weight
                    total_value += task_record.progress_rate
                    if task_record.stage_id.name == 'done':
                        closed_tasks_count += 1
                _logger.info(" #######T ####  %s",total_weight)
                _logger.info(" #######TV ####  %s",total_value2)
           
            if total_tasks_count > 0:
                _logger.info(" ##### TT ######  %s",total_weight)
                _logger.info(" #######TT VV####  %s",total_value2)

                if total_value > 0:
                    if (total_value2 / total_weight) > 0:
                        _logger.info("Total ----:%s",(total_value2 / total_weight))

                        record.progress = (total_value2 / total_weight)*100
                    else:
                        record.progress = (total_value / total_task)
                    _logger.info("Total From Div:%s",(total_value / total_task))
                    _logger.info("Total From weight:%s",(total_value2 / total_weight))

                
                else:
                    record.progress = (closed_tasks_count / total_tasks_count) * 100
            else:
                record.progress = 0.0
