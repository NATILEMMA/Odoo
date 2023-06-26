# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from datetime import datetime, timedelta
from odoo import api, models, _
from dateutil.relativedelta import relativedelta
from odoo.http import request



class PackingReportValues(models.AbstractModel):
    _name = "report.account_asset_management.asset_removal_template"

    @api.model
    def _get_report_values(self, docids, data=None):
        date = [{'date_from' :data['date_from'],'date_to':data['date_to']}]
        data = data['data']

        print("data",data,"date",date)
        return {
            'date':date,
            'data':data,
        }

        
 
