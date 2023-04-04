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

class ComplaintCategory(models.Model):
  _name="complaint.category"
  _description="These will hold a list of categories for complaints"

  name = fields.Char(required=True)
  wereda_id = fields.Many2one('membership.handlers.branch', string="Department")
  responsible_person = fields.Many2one(related='wereda_id.complaint_handler', string="Responsible Person")

class Complaints(models.Model):
  _name="member.complaint"
  _description = 'Member Complaints'
  _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
  _order = 'date_of_remedy'

  def _default_wereda(self):
    """This function will set a default value to wereda"""
    return self.env['membership.handlers.branch'].search([('complaint_handler', '=', self.env.user.id)], limit=1).id

  name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
  wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
  subcity_id = fields.Many2one('membership.handlers.parent')
  city_id = fields.Many2one('membership.city.handlers')
  subject = fields.Char(translate=True, track_visibility='onchange')
  victim_id = fields.Many2one('res.partner', domain="['&', '|', '|', ('subcity_id', '=', subcity_id), ('subcity_id.city_id', '=', city_id), ('wereda_id', '=', wereda_id), '|', '|', ('is_member', '=', True), ('is_league', '=', True), ('is_leader', '=', True)]")
  perpertrators = fields.Many2many('res.partner', domain="['|', ('is_member', '=', True), ('is_leader', '=', True)]")
  circumstances= fields.Text(translate=True, track_visibility='onchange')
  conclusion_report_wereda = fields.Text(translate=True, track_visibility='onchange')
  conclusion_report_subcity = fields.Text(translate=True, track_visibility='onchange')
  conclusion_report_city = fields.Text(translate=True, track_visibility='onchange')
  state = fields.Selection(string="Complaint status", selection=[('draft', 'Draft'), ('waiting for approval', 'Waiting For Approval'), ('transferred', 'Transferred'), ('transferred to city', 'Transferred to City'), ('resolved', 'Resolved'), ('rejected', 'Rejected'), ], default='draft', track_visibility='onchange')
  wereda_handler = fields.Many2one('res.users', readonly=True, store=True)
  subcity_handler = fields.Many2one('res.users', readonly=True, store=True)
  city_handler = fields.Many2one('res.users', readonly=True, store=True)
  duration_of_remedy = fields.Integer(default=30, store=True, track_visibility='onchange', readonly=True)
  date_of_remedy = fields.Date(store=True, track_visibility='onchange')
  duration_of_remedy_subcity = fields.Integer(default=30, store=True, track_visibility='onchange', readonly=True)
  date_of_remedy_subcity = fields.Date(store=True, track_visibility='onchange')
  duration_of_remedy_city = fields.Integer(default=30, store=True, track_visibility='onchange', readonly=True)
  date_of_remedy_city = fields.Date(store=True, track_visibility='onchange')
  x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
  transfer_1 = fields.Boolean(default=False)
  transfer_2 = fields.Boolean(default=False)
  transfer_3 = fields.Boolean(default=False)



  @api.model
  def create(self, vals):
    """This function will create a complaint"""
    if vals['wereda_id']:
      vals['wereda_handler'] = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])], limit=1).complaint_handler.id
    vals['name'] = self.env['ir.sequence'].next_by_code('member.complaint')
    res = super(Complaints, self).create(vals)
    res.date_of_remedy = res.create_date.date() +  timedelta(days=res.duration_of_remedy)
    return res

  def send_notification_to_wereda_complaint_handler(self):
    """This function will send notification to complaint handler"""
    future = date.today() + relativedelta(days=10)
    complaints = self.env['member.complaint'].search([('date_of_remedy', '=', future), ('state', '=', 'waiting for approval')])
    for complaint in complaints:
        model = self.env['ir.model'].search([('model', '=', 'member.complaint'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Complaint')], limit=1)
        activity = self.env['mail.activity'].sudo().create({
            'display_name': "Complaint Decision",
            'summary': "Evaluation",
            'date_deadline': future,
            'user_id': complaint.wereda_handler.id,
            'res_model_id': model.id,
            'res_id': complaint.id,
            'activity_type_id': activity_type.id
        })
        message = f"Complaint ID {complaint.name}'s Date of Remedy Is in 10 Days. Please Make A Decision Before It has To Be Transferred To Subcity Complaint Handler." 
        complaint.wereda_handler.notify_warning(message, '<h4>Complaint Decision</h4>', True)

  def send_to_subcity_complaint_handler(self):
    """This function will send complaint to subcity handler"""
    complaints = self.env['member.complaint'].search([('date_of_remedy', '=', date.today()), ('state', '=', 'waiting for approval')])
    for complaint in complaints:
        complaint.subcity_id = complaint.wereda_id.parent_id
        complaint.subcity_handler = complaint.subcity_id.complaint_handler
        complaint.state = 'transferred'
        complaint.transfer_1 = True
        model = self.env['ir.model'].search([('model', '=', 'member.complaint'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Complaint')], limit=1)
        activity = self.env['mail.activity'].sudo().create({
            'display_name': "Complaint Transfer",
            'summary': "Evaluation",
            'date_deadline': date.today() + relativedelta(days=10),
            'user_id': complaint.subcity_handler.id,
            'res_model_id': model.id,
            'res_id': complaint.id,
            'activity_type_id': activity_type.id
        })
        message = f"Complaint ID {complaint.name}'s Has Been Transfered To You. Please Make A Decision Before It has To Be Transferred To City Complaint Handler." 
        complaint.subcity_handler.notify_warning(message, '<h4>Complaint Decision</h4>', True)
        mail_temp = self.env.ref('members_custom.complaint_transfered_to_subcity')
        mail_temp.send_mail(complaint.id)

  def send_notification_to_subcity_complaint_handler(self):
    """This function will notiify subcity before transfer"""
    future = date.today() + relativedelta(days=10)
    complaints = self.env['member.complaint'].search([('date_of_remedy_subcity', '=', future), ('state', '=', 'transferred')])
    for complaint in complaints:
        model = self.env['ir.model'].search([('model', '=', 'member.complaint'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Complaint')], limit=1)
        activity = self.env['mail.activity'].sudo().create({
            'display_name': "Complaint Decision",
            'summary': "Evaluation",
            'date_deadline': future,
            'user_id': complaint.subcity_handler.id,
            'res_model_id': model.id,
            'res_id': complaint.id,
            'activity_type_id': activity_type.id
        })
        message = f"Complaint ID {complaint.name}'s Date of Remedy Is in 10 Days. Please Make A Decision Before It has To Be Transferred To City Complaint Handler." 
        complaint.subcity_handler.notify_warning(message, '<h4>Complaint Decision</h4>', True)

  def send_to_city_complaint_handler(self):
    """This function will send complaint to city handler"""
    complaints = self.env['member.complaint'].search([('date_of_remedy_subcity', '=', date.today()), ('state', '=', 'transferred')])
    for complaint in complaints:
        complaint.city_id = complaint.wereda_id.parent_id.city_id
        complaint.city_handler = complaint.city_id.complaint_handler
        complaint.state = 'transferred to city'
        complaint.transfer_2 = True
        complaint.transfer_1 = False
        model = self.env['ir.model'].search([('model', '=', 'member.complaint'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Complaint')], limit=1)
        activity = self.env['mail.activity'].sudo().create({
            'display_name': "Complaint Transfer",
            'summary': "Evaluation",
            'date_deadline': date.today() + relativedelta(days=10),
            'user_id': complaint.city_handler.id,
            'res_model_id': model.id,
            'res_id': complaint.id,
            'activity_type_id': activity_type.id
        })
        message = f"Complaint ID {complaint.name}'s Has Been Transfered To You. Please Make The Final Decision" 
        complaint.city_handler.notify_warning(message, '<h4>Complaint Decision</h4>', True)
        mail_temp = self.env.ref('members_custom.complaint_transfered_to_city')
        mail_temp.send_mail(complaint.id)


  def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
          if self.env.user.has_group('members_custom.member_group_agent') or self.env.user.has_group('members_custom.member_group_manager') or\
            self.env.user.has_group('members_custom.member_group_admin') or self.env.user.has_group('members_custom.member_group_city_transfer_handler') or\
            self.env.user.has_group('members_custom.member_group_city_admin') or self.env.user.has_group('members_custom.member_group_user_admin'):
            record.x_css = '<style> .o_form_button_create {display:None}</style>'
          elif self.env.user.has_group('members_custom.member_group_agent') or self.env.user.has_group('members_custom.member_group_manager') or\
            self.env.user.has_group('members_custom.member_group_admin') or self.env.user.has_group('members_custom.member_group_city_transfer_handler') or\
            self.env.user.has_group('members_custom.member_group_city_admin') or self.env.user.has_group('members_custom.member_group_user_admin'):
            record.x_css = '<style> .o_form_button_edit {display:None}</style>'
          elif (record.wereda_handler.id == self.env.user.id and record.transfer_1 == True) or (record.wereda_handler.id == self.env.user.id and record.transfer_2 == True):
              record.x_css = '<style> .o_form_button_edit {display:None}</style>'
          elif (record.wereda_handler.id == self.env.user.id or record.subcity_handler.id == self.env.user.id or record.city_handler.id == self.env.user.id) and\
              (record.state == 'rejected' or record.state == 'resolved'):
              record.x_css = '<style> .o_form_button_edit {display:None}</style>'
          elif record.subcity_handler.id == self.env.user.id and record.transfer_2 == True:
              record.x_css = '<style> .o_form_button_edit {display:None}</style>'
          else:
              record.x_css = False

  def waiting_for_approval(self):
    """This function will make complaint wait for approval"""
    for record in self:
      record.state = 'waiting for approval'

  def transfer_button(self):
    """This function will transfer complaint to subcity"""
    for record in self:
        record.subcity_id = record.wereda_id.parent_id
        record.subcity_handler = record.subcity_id.complaint_handler
        record.state = 'transferred'
        record.transfer_1 = True
        model = self.env['ir.model'].search([('model', '=', 'member.complaint'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Complaint')], limit=1)
        activity = self.env['mail.activity'].sudo().create({
            'display_name': "Complaint Transfer",
            'summary': "Evaluation",
            'date_deadline': date.today() + relativedelta(days=10),
            'user_id': record.subcity_handler.id,
            'res_model_id': model.id,
            'res_id': record.id,
            'activity_type_id': activity_type.id
        })
        message = f"Complaint ID {record.name}'s Has Been Transfered To You For Re-evaluation." 
        record.subcity_handler.notify_warning(message, '<h4>Complaint Decision</h4>', True)
        mail_temp = self.env.ref('members_custom.complaint_transfered_to_subcity')
        mail_temp.send_mail(record.id)

  def transfer_city_button(self):
    """This function will transfer complaint to subcity"""
    for record in self:
        record.city_id = record.wereda_id.parent_id.city_id
        record.city_handler = record.city_id.complaint_handler
        record.state = 'transferred to city'
        record.transfer_2 = True
        record.transfer_1 = False
        model = self.env['ir.model'].search([('model', '=', 'member.complaint'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Complaint')], limit=1)
        activity = self.env['mail.activity'].sudo().create({
            'display_name': "Complaint Transfer",
            'summary': "Evaluation",
            'date_deadline': date.today() + relativedelta(days=10),
            'user_id': record.city_handler.id,
            'res_model_id': model.id,
            'res_id': record.id,
            'activity_type_id': activity_type.id
        })
        message = f"Complaint ID {record.name}'s Has Been Transfered To You. Please Make The Final Decision" 
        record.city_handler.notify_warning(message, '<h4>Complaint Decision</h4>', True)   
        mail_temp = self.env.ref('members_custom.complaint_transfered_to_city')
        mail_temp.send_mail(record.id)   

  def send_pending_to_member(self):
      """This action will be able to send a pending complaint to a member"""
      mail_temp = self.env.ref('members_custom.complaint_waiting')
      for record in self:
        mail_temp.send_mail(record.id)
        message = f"Email has been sent to {record.victim_id.name} regarding the situation of Complaint ID {record.name}." 
        self.env.user.notify_success(message, '<h4>Email Sent</h4>', True)

  def send_review_to_member(self):
      """This action will be able to send a reviewed email to member"""
      mail_temp = self.env.ref('members_custom.complaint_review')
      for record in self:
        mail_temp.send_mail(record.id)
        message = f"Email has been sent to {record.victim_id.name} regarding the situation of Complaint ID {record.name}." 
        self.env.user.notify_success(message, '<h4>Email Sent</h4>', True)

  def complaint_resolved(self):
      """This function will handle the state change when a resolved button is clicked"""
      for record in self:
        if (record.conclusion_report_wereda and record.transfer_1 == False) or\
          (record.conclusion_report_subcity and record.transfer_1 == True) or\
          (record.conclusion_report_city and record.transfer_2 == True):
          record.state = 'resolved'
        else:
          raise ValidationError(_("Please fill in the conclusion report."))

  def complaint_rejected(self):
      """This function will handle the state change when rejected button is clicked"""
      for record in self:
        if (record.conclusion_report_wereda and record.transfer_1 == False) or\
          (record.conclusion_report_subcity and record.transfer_1 == True) or\
          (record.conclusion_report_city and record.transfer_2 == True):
            record.state = 'rejected'
        else:
            raise ValidationError(_("Please fill in the conclusion report."))

  @api.onchange('date_of_remedy')
  def _inverse_date_of_remedy(self):
      """This function will calculate the duration of remedy"""
      for record in self:
          if record.date_of_remedy:
              if record.date_of_remedy >= date.today():
                days = (record.date_of_remedy - date.today()).days
                record.duration_of_remedy = int(days)
              else:
                raise ValidationError(_('Pick A Date After The Date It Was Created'))

  @api.onchange('duration_of_remedy')
  def _compute_date_of_remedy(self):
      """This function will calculate the date of remedy"""
      for record in self:
          if record.duration_of_remedy:
              record.date_of_remedy = datetime.now() +  timedelta(days=record.duration_of_remedy)

  @api.onchange('date_of_remedy_subcity')
  def _inverse_date_of_remedy_subcity(self):
      """This function will calculate the duration of remedy"""
      for record in self:
          if record.date_of_remedy_subcity and record.create_date:
              if record.date_of_remedy_subcity >= record.create_date.date():
                days = (record.date_of_remedy_subcity - record.create_date.date()).days
                record.duration_of_remedy_subcity = int(days)
              else:
                raise ValidationError(_('Pick A Date After The Date It Was Created'))

  @api.onchange('duration_of_remedy_subcity')
  def _compute_date_of_remedy_subcity(self):
      """This function will calculate the date of remedy"""
      for record in self:
          if record.duration_of_remedy_subcity:
              record.date_of_remedy_subcity = datetime.now() +  timedelta(days=record.duration_of_remedy_subcity)


  @api.onchange('date_of_remedy_city')
  def _inverse_date_of_remedy_city(self):
      """This function will calculate the duration of remedy"""
      for record in self:
          if record.date_of_remedy_city and record.create_date:
              if record.date_of_remedy_city >= record.create_date.date():
                days = (record.date_of_remedy_city - record.create_date.date()).days
                record.duration_of_remedy_city = int(days)
              else:
                raise ValidationError(_('Pick A Date After The Date It Was Created'))

  @api.onchange('duration_of_remedy_city')
  def _compute_date_of_remedy_city(self):
      """This function will calculate the date of remedy"""
      for record in self:
          if record.duration_of_remedy_city:
              record.date_of_remedy_city = datetime.now() +  timedelta(days=record.duration_of_remedy_city)