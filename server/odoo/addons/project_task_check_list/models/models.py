# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import *
from dateutil.relativedelta import *
import time
import logging
_logger = logging.getLogger(__name__)


class CustomProject(models.Model):
    _inherit = 'project.task'
    check_box = fields.Boolean(string='Is Check List', default=False)
    info_checklist = fields.One2many(comodel_name="check.list", inverse_name="name", required=True,
                                     track_visibility='onchange')
    progress_rate = fields.Integer(string='Checklist Progress', compute="check_rate")
    total = fields.Integer(string="Max")
    status = fields.Selection(string="Status",
                              selection=[('done', 'Done'), ('progress', 'In Progress'), ('cancel', 'Cancel')],
                              readonly=True, track_visibility='onchange')

    maximum_rate = fields.Integer(default=100)
    weight = fields.Float(default="0",compute='_get_value_from_name', store=True)
    done_weight = fields.Float(default="0",compute='_get_weight', multi="progress", store=True)
    

    @api.depends('name')
    def _get_value_from_name(self):
        
        _logger.info("jjjjjjjjjjjjj")
        if self.name is not False:
            try:
                _logger.info("ssssssss:%s",type( self.name.start_date))
                date_start = datetime.strptime(str(self.name.start_date), '%Y-%m-%d').date()
                date_deadline = datetime.strptime(str(self.name.end_date), '%Y-%m-%d').date()
              
                # self.date_start = date_start
                month = self.name.start_date
                _logger.info("Month:%s",month)
                self.month = str(month.month)
                _logger.info("date_start:%s",date_start)
                _logger.info("date_deadline:%s",date_deadline)
                self.weight = self.name.weight
                # self.date_deadline = date_deadline

              
               
            except:
                pass




    @api.depends('info_checklist.work_done','info_checklist.status')
    def _get_weight(self):
        _logger.info("******work_done work_done***** %s",self.info_checklist)
        val = 0.0
        if self.info_checklist is False:
            pass
        else:
            try:
                for loop in self.info_checklist:
                    if loop.status == 'done':
                        work_done = (loop.work_done * loop.weight)/100
                        _logger.info("******work_done ***** %s",work_done)

                        val += work_done
                _logger.info(" ##### wwwwwwwwwwww ######  %s",val)
                self.done_weight = val
                _logger.info(" ###########  done_weightdone_weight %s",val)

            except:
                pass

    @api.onchange('info_checklist')
    def _get_weight_weight(self):
        _logger.info("*********** %s",self.info_checklist)
        _logger.info("*********** %s",self.weight)


        val = 0.0
        
        if self.info_checklist is False:
            pass
        else:
            for loop in self.info_checklist:
                work_done = (loop.work_done * loop.weight)/100
                _logger.info("******work_done ***** %s",loop.weight)

                val += loop.weight


                if val > self.weight:
                    raise UserError(_("The total weight of the checklist, which is %s, cannot be greater than the weight of the goal")% (str(val)))
                if work_done > loop.weight:
                    raise UserError(_("The percentage must be defined as 100%"))

                    # raise UserError(_("The Done value cannot be greater than the assigned weight"))

          
    # @api.onchange('weight')
    # def _get_weight_value(self):
    #     _logger.info("***** www ****** %s",self.weight)
    #     val = 0.0
    #     if self.weight is False:
    #         pass
    #     else:
    #         if self.weight > 10:
    #             pass
                # raise UserError(_('Warning! The weight value is not greater than 10'))

        
    def check_rate(self):
        _logger.info("***************")
        for rec in self:
            rec.progress_rate = 0
            total = len(rec.info_checklist.ids)
            done = 0
            cancel = 0
            value = 0.0
            # message = 'Create Work!'
            if total == 0:
                pass
            else:
                _logger.info("********else*******")

                if rec.info_checklist:
                    for item in rec.info_checklist:
                        if item.status == 'done':
                            done += 1
                            work_done = (item.work_done * item.weight)/100
                            _logger.info("***** weight****** %s",item.weight)
                            _logger.info("******* work_done**** %s",work_done)

                            value += work_done
                            # message = "Work: %s <br> Status: done" % (item.name_work)
                        if item.status == 'cancel':
                            cancel += 1
                            # message = "Work: %s <br> Status: cancel" % (item.name_work)
                        # if item.status == 'progress':
                        #     message = "Work: %s <br> Status: In Progress" % (item.name_work)
                    _logger.info("valus %s",value)
                    
                    if value == 0.0:
                        rec.progress_rate = 0
                    else:
                        _logger.info("valus %",value)

                        rec.progress_rate = round((float(value) / float(rec.weight)) * 100)
                    # rec.message_post(body=message)
