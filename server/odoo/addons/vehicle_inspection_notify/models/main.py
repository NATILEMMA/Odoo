from odoo import _, api, models, fields
import logging
import datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, Warning
from datetime import datetime, timedelta


class InspectionDate(models.Model):
    _inherit = "vehicle.libre"

    issue_date = fields.Datetime(string="Next Inspection Date", required=True, store=True)
    inspect_date = fields.Datetime(string="last Inspection Date", required=True, store=True)
    notify_date = fields.Datetime(string="Notify Date", compute='_compute_date', readonly=True, store=True)
    sticker_number = fields.Char(string="Annual Sticker Number")
    approver = fields.Many2one('res.partner', string="Approver")
    user_id = fields.Many2one('res.users', string="User")

    @api.depends('issue_date', 'notify_date')
    def _compute_date(self):
        for order in self:

            dates_list = order.issue_date
            _logger.info(dates_list)

            if dates_list:
                order.notify_date = dates_list

    def action_notify_odoo(self):
        current_date = datetime.today().date()
        minimized_date = current_date + relativedelta(days=15)
        max_date = current_date + relativedelta(days=16)
        conv_date = datetime.combine(minimized_date, datetime.min.time())
        conv_date_2 = datetime.combine(max_date, datetime.min.time())
        libre = self.env['vehicle.libre'].search(
            [('issue_date', '>', conv_date), ('issue_date', '<', conv_date_2)])
        print("conv_date_2", conv_date_2)
        for lib in libre:
            user_id = lib.user_id
            print("user_id", user_id)
            model = self.env['ir.model'].search([('model', '=', 'vehicle.libre')])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Libray update mail')], limit=1)
            message = str(lib.vehicle_id.name) + "'s with in 15 days libre need to be renewal."
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "renewal",
                'date_deadline': conv_date_2,
                'user_id': user_id.id,
                'res_model_id': model.id,
                'res_id': lib.id,
                'activity_type_id': activity_type.id
            })
            user_id.notify_warning(message, '<h4>Candidate Approval</h4>', True)
