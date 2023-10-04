import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"


    ethiopian_from = fields.Date(string="From Date", store=True) # leave_date_from
    pagum_from = fields.Char(string="From Date", store=True)
    is_pagum_from = fields.Boolean(default='True', string="From Date")


    ethiopian_to = fields.Date(string="To Date", store=True) # leave_date_to
    pagum_to = fields.Char(string="To Date", store=True)
    is_pagum_to = fields.Boolean(default='True', string="To Date")


    def _compute_leave_status(self):
        res = super(HrEmployeeBase, self)._compute_leave_status()

        try:
            if self.leave_date_from:
                date1 = self.leave_date_from
                date_time_obj1 = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj1[0]), int(date_time_obj1[1]),
                                                int(date_time_obj1[2]))

                if type(Edate1) == date:
                    self.ethiopian_from = Edate1

                elif type(Edate1) == str:
                    self.pagum_from = Edate1
                    self.is_pagum_from = False
        except:
            pass

        try:
            if self.leave_date_to:
                date2 = self.leave_date_to
                date_time_obj2 = date2.split('-')

                Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]), int(date_time_obj2[1]),
                                                                int(date_time_obj2[2]))

                if type(Edate2) == date:
                    self.ethiopian_to = Edate2
                elif type(Edate2) == str:
                    self.pagum_to = Edate2
                    self.is_pagum_to = False
        except:
            pass

        return res


# class User(models.Model):
#     _inherit = "res.users"


#     ethiopian_to = fields.Date(string="To Date", store=True, related="employee_id.ethiopian_to") # leave_date_to
#     pagum_to = fields.Char(string="To Date", store=True, related="employee_id.pagum_to")
#     is_pagum_to = fields.Boolean(default='True', string="To Date", related="employee_id.is_pagum_to")