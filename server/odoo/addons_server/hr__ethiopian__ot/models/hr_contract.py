from odoo import models, fields


class Contract(models.Model):
    _inherit = 'hr.contract'

    def _compute_wage(self):
        for recd in self:
            wage = recd.wage
            resource_calendar = recd.resource_calendar_id 
            schedule = resource_calendar.attendance_ids
            working_hours = 0
            for work_period in schedule:
                working_hours += (work_period.hour_to - work_period.hour_from)
                
            if resource_calendar.two_weeks_calendar:
                recd.over_hour = wage/(working_hours*2)
            else:
                recd.over_hour = wage/(working_hours*4)
                

    over_hour = fields.Float('Hour Wage', compute='_compute_wage')
    can_work_on_shift = fields.Boolean(string="Can Work On Shift")
