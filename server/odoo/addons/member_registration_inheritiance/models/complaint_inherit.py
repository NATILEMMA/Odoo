"""This function will create a complain form"""


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta,datetime, date
from dateutil.relativedelta import relativedelta
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
dates = []
dd,mm,yy=0,0,0


class Complaints(models.Model):
  _inherit="member.complaint"

  victim_id = fields.Many2one('res.partner', domain="['&', '|', '|', ('is_league', '=', True), ('is_member', '=', True), ('is_leader', '=', True), '&', '|', ('member_cells', '!=', False), ('league_member_cells', '!=', False), '|', '|', ('subcity_id.city_id', '=', city_id), ('subcity_id', '=', subcity_id), ('wereda_id', '=', wereda_id)]")

  def send_pending_to_member(self):
      """This action will be able to send a pending complaint to a member"""
      mail_temp = self.env.ref('complaint_waiting')
      for record in self:
        mail_temp.send_mail(record.id)
        message = _("Email has been sent to %s regarding the situation of Complaint ID %s.") % (record.victim_id.name, record.name)
        title = _("<h4>Email Sent</h4>")
        self.env.user.notify_success(message, title, True)

  def send_review_to_member(self):
      """This action will be able to send a reviewed email to member"""
      mail_temp = self.env.ref('complaint_review')
      for record in self:
        mail_temp.send_mail(record.id)
        message = _("Email has been sent to %s regarding the situation of Complaint ID %s.") % (record.victim_id.name, record.name)
        title = _("<h4>Email Sent</h4>")
        self.env.user.notify_success(message, title, True)
