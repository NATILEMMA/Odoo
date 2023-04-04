from odoo import _, api, models, fields
import logging
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError,Warning 
from datetime import datetime, timedelta


class InspectionDate(models.Model):
    _inherit = "vehicle.libre"


    issue_date = fields.Datetime(string="Inspection Date", required=True, store=True)
    notify_date = fields.Datetime(string="Notify Date", compute='_compute_date', readonly=True, store=True)
    sticker_number=fields.Char(string="Annual Sticker Number")
    approver = fields.Many2one('res.users', string="Approver")
    user_id = fields.Many2one('res.users', string="User")

    @api.depends('issue_date','notify_date')
    def _compute_date(self):
        for order in self:
          
            dates_list = order.issue_date
            _logger.info(dates_list)
           
            if dates_list:               
                order.notify_date = dates_list


    def action_notify_odoo(self):

        values = self.env['vehicle.libre'].search([('user_id','!=',False)])
        # values = self.env['vehicle.libre'].search([])
        _logger.info(len(values))
        
        if len(values) != 0:            
            val = []
            Ex_val = []

            for n in range(len(values)):
                    notify_date = values[n].notify_date
                    issue_date = values[n].issue_date
                    
                    if(issue_date and notify_date != False):     
                        date_difference = issue_date-datetime.now()
                        _logger.info(date_difference)
                        _logger.info("--------------Inspection date------------------------")
                        today = datetime.now()
                        date, time = str(today).split(" ")
                        ex_d, time = str(notify_date).split(" ")
                        _logger.info(f"{date}")
                        _logger.info(f"{ex_d}")
                        if f"{date}" == f"{ex_d}":
                            _logger.info("Inspection date diff value zero")
                            break
                        else:
                            day, time  = str(date_difference).split(",")
                            d = f"{day}"
                            _logger.info(d)
                            da, days = str(d).split(" ")
            
                            days = f"{da}"
                            last_days = 9 - int(days)
                            last_days = str(last_days)
                            _logger.info(days)
                            
                            
                            if int(days) >= 1 and int(days) < 7:
                                for l in values[n]:
                                    _logger.info(l.user_id.name)
                                    val.append((days,l.user_id.name,values[n].user_id,values[n].user_id.name,values[n].notify_date))#,values[n].product_id.name,values[n].user_id)
                                    _logger.info(val) 
                              
                            
            _logger.info("----------------last day-------")
            _logger.info(val)
           
            for x in val:
                notify = 'You Have <h3><i>' + x[0] +  ' days left  </i><span style="margin-left: 80px;"> Ins: '+ x[3]+'</span></h3>' + 'Inspection Date <b>' + str(x[4])+ '</b> <br>Owner =  <b><i>' + x[1] + '</i></b>'
                
                x[2].notify_warning(notify,"<h3><b>Inspection Date Alert</b></h3>-",True)
           
 
        
                       
            

    
  