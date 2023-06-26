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
    _name = "report.employee_orientation.print_pack_template"

    @api.model
    def _get_report_values(self, docids, data=None):

        lst = []
        if(docids):
            docs = self.env['employee.training'].browse(docids[0])          
            for doc in docs:
                started_date = datetime.strftime(doc.create_date, "%Y-%m-%d ")
                duration = (doc.write_date - doc.create_date).days
                pause = relativedelta(hours=0)
                difference = relativedelta(doc.write_date, doc.create_date) - pause
                hours = difference.hours
                minutes = difference.minutes
                for emp in doc.training_id:
                    lst.append({
                    'name': emp.name,
                    'date_to': started_date,
                    'duration': duration,
                    'hours': hours,
                    'minutes': minutes,
                    'company_name': doc.company_id.name,
                    'dept_id': doc.program_department.id,
                    'program_name': doc.program_id.name,
                    'program_round': doc.program_round_id.name,  
                    'institution':doc.instution_id.name,
                    'program_convener': doc.program_convener.name,
                })
            return {
                'docids':docids,
                'docs':docs,
                'data': lst,
            }

        
 
