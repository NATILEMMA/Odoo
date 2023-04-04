"""This function will customize the hr_employees"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta




class EmployeeBaseInherit(models.AbstractModel):
    _inherit = "hr.employee.base"


    @api.model 
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(EmployeeBaseInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'remaining_leaves' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_remaining_leaves = 0.0
                    for record in lines:
                        total_remaining_leaves += record.remaining_leaves
                    line['remaining_leaves'] = total_remaining_leaves

        return res


class Contract(models.Model):
    _inherit="hr.contract"


    start_date_for_approval = fields.Date(store=True)