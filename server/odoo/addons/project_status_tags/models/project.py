# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime, timedelta
from datetime import *
from dateutil.relativedelta import *
import time
from odoo import models, tools, _
from odoo.exceptions import UserError
import logging
# from datetime import datetime, date 
# from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
_logger = logging.getLogger(__name__)


_TASK_STATE = [('draft', 'New'),
               ('open', 'In Progress'),
               ('pending', 'Pending'),
               ('done', 'Done'),
               ('cancelled', 'Cancelled')
               ]


class Project(models.Model):
    _inherit = 'project.project'

    project_status = fields.Selection(compute='_project_task_status', method=True,
                                      selection=[
                                          ('on_track', 'On Track'),
                                         ('requested', 'Requested'),
                                          ('off_track', 'Delayed'),
                                          ('at_risk', 'At Risk'),
                                          ('onhold', 'On Hold'),
                                          ('done', 'Completed'),
                                          ('not_active', 'Not Active'),
                                          ('cancelled', 'Cancelled')
                                      ], string='Planning Status', track_visibility='onchange',store=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('close', 'Completed'),
        ('cancelled', 'Cancelled')],
        'Status', copy=False, default='draft', track_visibility='onchange')
    status_color = fields.Integer(compute='_check_color', method=True, string='Colour',store=True)
    projected_date_end = fields.Date(compute='_get_projected_date_end', method=True, string="Projected End Date", store=True, default=time.strftime('%Y-%m-%d'))
    actual_date_start = fields.Date('Actual Starting Date', copy=False)
    actual_date_end = fields.Date('Actual Ending Date', copy=False)
    planned_hours = fields.Float(compute='_hours_get', multi="progress", string='Planned Time', store=True)
    effective_hours = fields.Float(compute='_hours_get', multi="progress", string='Time Spent', store=True)
    total_hours = fields.Float(compute='_hours_get', multi="progress", string='Total Time', store=True)
    progress_rate = fields.Float(compute='_hours_get', multi="progress", string='Progress', group_operator="avg", store=True)
    date_start = fields.Date(string='Start Date', default=fields.Datetime.now().date(), track_visibility='onchange')
    date = fields.Date(string='End Date', index=True, track_visibility='onchange', default=fields.Datetime.now().date())

    
    
    def action_reset(self):
        self.state = "draft"

        super(Project, self).write({'state':'draft'}) 
    # def action_request(self):
    #     self.state = "requested"
    #     self._project_task_status()
    #     super(Project, self).write({'state':'requested'}) 
         
    # def action_reject(self):
    #     self.state = "cancelled"
    #     self._project_task_status()
    #     super(Project, self).write({'state':'cancelled'})
    # def action_approve(self):
    #     self.state = "approved"
    #     self._project_task_status()
    #     super(Project, self).write({'state':'approved'})
        

    @api.depends('state', 'date_start', 'date', 'projected_date_end')
    def _project_task_status(self):
        for val in self:
            _logger.info(val.project_status)
            _logger.info(val.state)

            project_status = False
            if val.date_start and val.date:
                date_start = val.date_start
                date_end = val.date
                pr_end_date = val.projected_date_end
                today = datetime.now().date()
                if val.state == 'draft':
                    project_status = 'not_active'
                if val.state == 'requested':
                    project_status = 'requested'
                if val.state == 'approved':
                    project_status = 'on_track'
                if val.state == 'open':
                    project_status = 'on_track'
                if val.state == 'pending':
                    project_status = 'onhold'
                if val.state == 'open' and today >= (date_end + relativedelta(days=-2)):
                    project_status = 'at_risk'
                if not val.state == 'pending' and datetime.now().date() > date_end:
                    project_status = 'off_track'
                if val.state == 'close':
                    project_status = 'done'
                else:
                    if val.actual_date_start and val.actual_date_end:
                        project_status = 'done'
                    elif val.state == 'cancelled':
                        project_status = 'cancelled'
                    elif (not val.actual_date_start and (date_start > datetime.now().date())):
                        project_status = 'onhold'
                val.project_status = project_status

    @api.depends('project_status')
    def _check_color(self):
        for val in self:
            # project_status = False
            color = 0
            if val.project_status == u'on_track':
                color = 1
            elif val.project_status == u'off_track':
                color = 2
            elif val.project_status == u'at_risk':
                color = 3
            elif val.project_status == u'onhold':
                color = 4
            elif val.project_status == u'done':
                color = 5
            elif val.project_status == u'cancelled':
                color = 6
            elif val.project_status == u'not_active':
                color = 7
            elif val.project_status == u'requested':
                color = 9
            val.status_color = color

    @api.depends('date_start','date')
    def _get_projected_date_end(self):
        for val in self:
            projected_date_end = False
            today = datetime.now().date()
            if val.date and val.date_start:
                diff_days = (val.date - val.date_start).days or 0
                _logger.info("diff_days day %s",diff_days)

                if not val.actual_date_start:
                    if today <= val.date_start:
                        projected_date_end = val.date
                    elif today > val.date_start:
                        projected_date_end = today + timedelta(days=int(diff_days))
                    else:
                        projected_date_end = val.date
                else:
                    if val.state not in ('draft', 'cancelled'):
                        progress = 1 - (val.progress_rate / 100)
                        progress_days = str(int(round(abs(progress * diff_days))))
                        projected_date_end = today + timedelta(days=int(progress_days))
                    else:
                        projected_date_end = val.date
            _logger.info("projected_date_end day %s",projected_date_end)

            val.projected_date_end = projected_date_end

    def _check_tasks(self):
        task_br = self.env['project.task']
        task_search = task_br.search([('project_id', '=', self.id)])
        if task_search:
            for task in task_search:
                if task.state not in ('done', 'cancelled', 'pending'):
                   raise UserError(_('Warning! \n Task - %s is currently cannot complete, cancel, or put this project on hold until the tasks associated with it are completed or cancelled.') %(str(task.name.name )))
        return True

    @api.onchange('date_start','date')
    def onchange_check_date(self):
        if self.date_start and self.date:
            if self.date_start > self.date:
               raise UserError(_('Start Date cannot be lesser than End Date'))
    def action_request(self):
        self.state = "requested"
        self._project_task_status()
        self.write({'state': 'requested', 'actual_date_end': datetime.now(), 'project_status': 'requested'})


         
    def action_reject(self):
        self.state = "cancelled"
        self._project_task_status()
        self.write({'state': 'cancelled', 'actual_date_end': datetime.now(), 'project_status': 'cancelled'})

    def action_approve(self):
        self.state = "approved"
        self._project_task_status()
        self.write({'state': 'approved', 'actual_date_end': datetime.now(), 'project_status': 'on_track'})


    def set_cancel(self):
        self._check_tasks()
        self._project_task_status()
        if self.state in 'open':
            self.write({'state': 'cancelled'})

    def start_project(self):
        self._project_task_status()
        date1 = datetime.now()
        date_time_obj = str(date1).split(' ')
        date_time_obj = date_time_obj[0].split('-')

        Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
        _logger.info("^^^^^^^^^^^ %s",type(Edate1))
        self.actual_date_start = date1
        if type(Edate1) == str:
            self.ethiopian_three = None
            self.is_pagum_three = False
            self.pagum_three = Edate1
            self.state = 'open'
        elif type(Edate1) == date:
            self.ethiopian_three = Edate1
            self.is_pagum_three = True
            self.pagum_three = ' '
            self.state = 'open'



        # self.write({'state': 'open', 'actual_date_start': datetime.now()})

    def set_done(self):
        self._check_tasks()
        self._project_task_status()
        date1 = datetime.now()
        _logger.info("^^^^^^^^^^^ %s",date1)

        date_time_obj = str(date1).split(' ')
        date_time_obj = date_time_obj[0].split('-')

        Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
        _logger.info("^^^^^^^^^^^ %s",type(Edate1))
        self.actual_date_end = date1
        if type(Edate1) == str:
            self.ethiopian_four = None
            self.is_pagum_four = False
            self.pagum_four = Edate1
            self.state = 'close'
        elif type(Edate1) == date:
            self.ethiopian_four = Edate1
            self.is_pagum_four = True
            self.pagum_four = ' '
            self.state = 'close'
        # self.write({'state': 'close', 'actual_date_end': datetime.now(), 'project_status': 'done'})

    def set_pending(self):
        self._project_task_status()
        self.write({'state': 'pending'})

    def set_open(self):
        self._project_task_status()
        self.write({'state': 'open'})

    def reset_project(self):
        self._project_task_status()
        self.write({'state': 'open'})

    # set active value for a project, its sub projects and its tasks
    def setActive(self, value=True):
        self._project_task_status()
        task_obj = self.env['project.task']
        for proj in self:
            self.write({'state': value and 'open'})
            self._cr.execute('select id from project_task where project_id=%s', (proj.id,))
            tasks_id = [x[0] for x in self._cr.fetchall()]
            if tasks_id:
                task_obj.write({'active': value})
        return True

    @api.depends('task_ids.planned_hours', 'task_ids.effective_hours')
    def _hours_get(self):
        for project in self:

            for task in project.task_ids:
                project.planned_hours += task.planned_hours
                project.total_hours = project.planned_hours
                for work_time in task.timesheet_ids:
                    project.effective_hours += work_time.unit_amount

                if task.stage_id and task.stage_id.fold:
                    project.progress_rate = 100.0
                elif (project.planned_hours > 0.0):
                    project.progress_rate = round(100.0 * (project.effective_hours) / project.planned_hours, 2)
                else:
                    project.progress_rate = 0.0

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        stage_project_task = self.env['project.task.type']
        stage_project_search = stage_project_task.search([])
        for i in stage_project_search:
            if i.state:
                i.update({
                    'project_ids': [(4, res.id)]
                })
        return res


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    state = fields.Selection(_TASK_STATE, 'Related Status')


class Task(models.Model):
    _inherit = 'project.task'

    # @api.model
    # def _get_default_partner(self):
    #     _logger.info("DDDDDDDDDDDDDDDDDD %s",self.proje)
    #     _logger.info("DDDDDDDDDDDDDDDDDD %s",self.user_id)

    #     if self.project_id:
    #         default_project_id = self.env['project.project'].browse(self.env.context['default_project_id'])
    #         date = datetime.now()
    #         return False

    # date_end = fields.Datetime(string='Start Date', index=True, default=lambda self: self._get_default_date(),copy=False)
    # date_end = fields.Datetime(string='Ending Date', index=True, cdefault=lambda self: self._get_default_date(),opy=False)

    def _check_project(self):
        for i in self:
            if i.project_id:
                if i.project_id.state != 'open':
                   raise UserError(_('Warning! \n Your %s  is in draft state,  so you cannot start this task.\n Please activate your planning first')%(str(i.project_id.name )))
        return True

    def days_between(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days) + 1

    @api.depends('project_id.state', 'state', 'date_start', 'date_end', 'date_deadline', 'projected_date_end')
    def _get_task_status(self):
        _logger.info("############# Under Task Status")
        for val in self:
            status = ''
            if val.date_start and val.date_deadline:
                date_start = val.date_start
                date_end = val.date_deadline
                pr_end_date = val.projected_date_end
                today = datetime.now().date()
                _logger.info(val.state)
                _logger.info(self.project_id.task_ids)
                try:
                    if val.state not in ('open', 'pending', 'done'):
                        status = 'not_active'
                    if val.state == 'draft':
                        status = 'not_active'
                    if val.state == 'open':
                        status = 'on_track'
                    if val.state == 'pending':
                        status = 'onhold'
                    # if val.state == 'open':
                    #     status = 'at_risk'
                    # if not val.state == 'pending':
                    #     status = 'off_track'
                    if val.project_id and val.state in ('done'):
                        status = 'done'
                    else:
                        if val.actual_date_start and val.actual_date_end:
                            status = 'done'
                        elif val.state == 'cancelled':
                            status = 'cancelled'
                        elif (not val.actual_date_start and (date_start > datetime.now().date())):
                            status = 'onhold'
                    val.task_status = status
                except:
                   raise UserError(_("You cannot move the task until the parent planning is in the Start state. Please start your planning first."))

    @api.depends('task_status')
    def _check_color(self):
        for record in self:
            color = 0
            if record.task_status == u'on_track':
                color = 1
            elif record.task_status == u'off_track':
                color = 2
            elif record.task_status == u'at_risk':
                color = 3
            elif record.task_status == u'onhold':
                color = 4
            elif record.task_status == u'done':
                color = 5
            elif record.task_status == u'cancelled':
                color = 6
            elif record.task_status == u'not_active':
                color = 7
            elif record.task_status == u'requested':
                color = 8
            record.status_color = color

    def write(self, vals):
        _logger.info("######################## %s",self.kanban_state)
        _logger.info("############# project_id ########### %s",self.project_id.state)
        _logger.info("############# task ########### %s",self.stage_id.state)

        if self.project_id.state == 'draft':
            # for i in self:
            #     if i.project_id:
            #         if i.project_id.state != 'open':
            #             raise UserError(_('Warning! \n Your %s  is in draft state,  so you cannot start this task.\n Please activate your planning first')%(str(i.project_id.name )))
            # pass
            if self.stage_id.state == 'open' or self.stage_id.state == 'pending':
                self.stage_id.state == 'draft'
            
                raise UserError(_('Warning! \n Your %s  is in draft state,  so you cannot move this task.\n Please activate your planning first')%(str(self.project_id.name )))

        if vals.get('stage_id'):
            if self.kanban_state == 'blocked':
                #raise UserError(_(('You can modify the task which is ' + self.state + ' ' +'but its reviewed result not success'))
                vals.update({'state': self.stage_id.state})
            else:
                if self.state in ('done'):
                   raise UserError(_('You cannot modify the task which is Done'))
                elif self.state in ('cancelled'):
                   raise UserError(_('You cannot modify the task which is cancelled'))
                else:
                    pass
            vals.update({'state': self.env['project.task.type'].browse(vals.get('stage_id')).state})
        if vals.get('sequence'):
            vals.update({'state': self.stage_id.state})
        if vals.get('state') == 'open':
            vals.update({'actual_date_start': datetime.now()})
        if vals.get('state') == 'done':
            vals.update({'actual_date_end': datetime.now()})
        if vals.get('state') != 'done':
            vals.update({'actual_date_end': False})
        if vals.get('state') == 'draft':
            vals.update({'actual_date_start': False})
        if vals.get('state') == 'done' and not vals.get('actual_date_start'):
            vals.update({'actual_date_start': datetime.now()})
        if vals.get('date_start'):
            # date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if self.project_id.date_start:
                if self.date_start < self.project_id.date_start:
                   raise UserError(_('Task start date cannot be greater than the project starting date %s') %(str(self.project_id.date_start)))
        if vals.get('date_deadline') and self.date_start:
            # deadline = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            _logger.info("deadline 333333 %s",self.date_start )
            _logger.info("deadline 333333 %s",self.date_deadline )

            if self.date_deadline < self.date_start:
               raise UserError(_('Deadline cannot be lesser than the starting date'))
        if self.date_deadline and vals.get('date_start'):
            # date_start = datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if self.date_deadline < self.date_start:
               raise UserError(_('Deadline cannot be lesser than the starting date %s') %(str(self.date_deadline) )) 
        # if vals.get('date_deadline'):
        #     if self.project_id.date:
        #         prj_end_date = self.project_id.date

        #         _logger.info("date_deadline %s",vals.get('date_deadline'))
        #         _logger.info("prj_end_date %s",prj_end_date)


        #         _logger.info("date_deadline %s",type(vals.get('date_deadline')))
        #         _logger.info("prj_end_date %s",type(prj_end_date))
        #         date_deadline = vals.get('date_deadline') #datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
              

        #         if prj_end_date < date_deadline:
        #            raise UserError(_('Deadline cannot be greater than the project end date %s') %( str(self.project_id.date) ))
        res = super(Task, self).write(vals)
        return res

    @api.depends('date_start','date_deadline')
    def _get_projected_date_end(self):
        for val in self:
            if val.date_deadline and val.date_start:
                projected_date_end = False
                diff_days = 0
                today = datetime.now().date()
                start_date = datetime.strftime(val.date_start, "%Y-%m-%d")
                end_date = datetime.strftime(val.date_deadline, "%Y-%m-%d")
                if val.date_start and val.date_deadline:
                    diff_days = abs(datetime.strptime(start_date, "%Y-%m-%d") - datetime.strptime(end_date, "%Y-%m-%d")).days
                if not val.actual_date_start:
                    if today <= val.date_start:
                        projected_date_end = val.date_deadline
                    elif today > val.date_start and diff_days:
                        projected_date_end = str(today + timedelta(days=int(diff_days)))
                    else:
                        projected_date_end = val.date_deadline
                else:
                    if val.state not in ('draft', 'cancelled'):
                        progress = 1 - (val.progress / 100)
                        progress_days = str(int(round(abs(progress * diff_days))))
                        projected_date_end = today + timedelta(days=int(progress_days))
                    else:
                        projected_date_end = val.date_deadline
                val.projected_date_end = projected_date_end

    def _get_default_stage_id(self):
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', False)]):
            if stage_search:
                pass
                #raise UserError(_(('Kindly configure your stages with the related status field'))
        return True

    @api.model
    def create(self, vals):
        _logger.info("VVVVVVVVVVVVV %s",vals)
        if vals.get('date_deadline'):
            date_deadline = vals.get('date_deadline') #datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            date_start = vals.get('date_start') #datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if date_deadline < date_start:
               raise UserError(_('Deadline cannot be lesser than the starting date'))
        if vals.get('project_id'):
            project_end_date = self.env['project.project'].browse(vals.get('project_id')).date
            if not project_end_date:
               raise UserError(_('Kindly Fill the Planning End Date'))
            date_deadline = vals.get('date_deadline') #datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').date()
            starting_dt = vals.get('date_start') #datetime.strptime(vals.get('date_start'), '%Y-%m-%d').date()
            if vals.get('date_start'):
                project_starting_date = self.env['project.project'].browse(vals.get('project_id')).date_start
                if project_starting_date > starting_dt:
                   raise UserError(_('Task start date cannot be greater than the project starting date %s') % (str(self.env['project.project'].browse(vals.get('project_id')).date_start)))
            if project_end_date < date_deadline:
               raise UserError(_('Deadline cannot be greater than the project end date %s') % (str(self.env['project.project'].browse(vals.get('project_id')).date)))
        return super(Task, self).create(vals)

    def unlink(self):
        for i in self:
            if i.state != 'draft':
               raise UserError(_('Warning! You cannot delete a created task'))
        return super(Task, self).unlink()

    task_status = fields.Selection(compute='_get_task_status', method=True,
                                   selection=[
                                       ('on_track', 'On Track'),
                                       ('requested', 'Requested'),
                                       ('off_track', 'Delayed'),
                                       ('onhold', 'On Hold'),
                                       ('at_risk', 'At Risk'),
                                       ('future', 'Future'),
                                       ('done', 'Completed'),
                                       ('cancelled', 'Cancelled'),
                                       ('new', 'New'),
                                       ('not_active', 'Not Active')
                                   ], string='Task Status', track_visibility='onchange',store=True)
    status_color = fields.Integer(compute='_check_color', string='Colour', method=True,store=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled')], string="Status", readonly=False, store=True,
        help='The status is set to \'Draft\', when a case is created.\
                      If the case is in progress the status is set to \'Open\'.\
                      When the case is over, the status is set to \'Done\'.\
                      If the case needs to be reviewed then the status is \
                      set to \'Pending\'.', default='draft')
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
                               default=_get_default_stage_id,
                               group_expand='_read_group_stage_ids',
                               domain="[('project_ids', '=', project_id)]", copy=False)
    date_start = fields.Date('Starting Date', copy=False, track_visibility='onchange', default=fields.Datetime.now().date())
    projected_date_end = fields.Date(compute='_get_projected_date_end', method=True, string="Projected End Date", store=True)
    actual_date_start = fields.Date('Actual Starting Date', copy=False)
    actual_date_end = fields.Date('Actual Ending Date', copy=False)
    progress_status = fields.Boolean('Progress Status', copy=False)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, track_visibility='onchange', default=time.strftime('%Y-%m-%d'))

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_start = fields.Datetime.now().date()

    @api.onchange('date_start','date_deadline')
    def onchange_check_date(self):
        if self.date_start and self.date_deadline:
            if self.date_start > self.date_deadline:
               raise UserError(_('Start Date cannot be lesser than deadline'))

    def start_task(self):
        self._check_project()
        stage_obj = self.env['project.task.type'].search([])
        _logger.info("############ state %s",self.state)

        _logger.info("############ stage_obj %s",stage_obj)
        active_id =self._context.get('active_id')
        _logger.info("3333333333 %s",stage_obj.search([('name', '=', 'open')]))
        for lo in stage_obj:
            _logger.info("***********v %s",lo.name)
            _logger.info("***********State %s",lo.state)
        st = stage_obj.search([('name', '=', 'open')])
        for stage_search in stage_obj.search([('name', '=', 'open')]):
            _logger.info("############ stage_search %s",stage_search)

        # self.write({'stage_id': st.id, 'state': 'open', 'actual_date_start': datetime.now()})
        super(Task, self).write({'stage_id': st.id, 'state': 'open', 'actual_date_start': datetime.now()})


    def set_open(self):
        self._check_project()
        stage_obj = self.env['project.task.type']

        for stage_search in stage_obj.search([('state', '=', 'open')]):
            self.write({'stage_id': stage_search.id, 'state': 'open'})

    def set_done(self):
        self._check_project()
        if self.state == 'draft':
           raise UserError(_('You cannot completed the task if the task has not been started'))
        stage_obj = self.env['project.task.type'].search([('state', '=', 'done')])
        for stage_search in stage_obj.search([('state', '=', 'done')]):
            self.write({'stage_id': stage_search.id, 'state': 'done', 'actual_date_end': datetime.now()})

    def set_cancel(self):
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', 'cancelled')]):
            self.write({'stage_id': stage_search.id, 'state': 'cancelled'})

    def set_pending(self):
        self._check_project()
        stage_obj = self.env['project.task.type']
        for stage_search in stage_obj.search([('state', '=', 'pending')]):
            self.write({'stage_id': stage_search.id, 'state': 'pending'})
