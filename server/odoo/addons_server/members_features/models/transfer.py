"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta



class Transfer(models.Model):
   _name="members.transfer"
   _description="Member Transfer"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_cell(self):
      """This function will set a default value to wereda"""
      cell = self.env['member.cells'].search([('cell_admin', '=', self.env.user.id), ('state', '=', 'active')], limit=1)
      if cell:
         return cell.id
      else:
         return 0

   def _default_main_office(self):
      """This function will set a default value to wereda"""
      main_office = self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1)
      if main_office:
         return main_office.id
      else:
         return 0


   def _default_wereda(self):
      """This function will set a default value to wereda"""
      wereda = self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1)
      if wereda.id:
         return wereda.id
      else:
         return 0

   def _default_subcity(self):
      """This function will set a default value to wereda"""
      subcity = self.env['membership.handlers.parent'].search([('parent_manager', '=', self.env.user.id)], limit=1)
      if subcity:
         return subcity.id
      else:
         return 0

   def _default_city(self):
      """This function will set a default value to wereda"""
      city = self.env['membership.city.handlers'].search([('city_manager', 'in', [self.env.user.id])], limit=1)
      if city:
         return city.id
      else:
         return 0


   name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
   city_id = fields.Many2one('membership.city.handlers', default=_default_city)
   subcity_id = fields.Many2one('membership.handlers.parent', default=_default_subcity)
   wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
   main_office_id = fields.Many2one('main.office', default=_default_main_office)
   cell_id = fields.Many2one('member.cells', default=_default_cell)
   correct_user = fields.Boolean(default=False)
   membership_status = fields.Char(default="Full Member", readonly=True)
   transfer_league_responsibility = fields.Many2one('league.responsibility', track_visibility='onchange')
   transfer_responsibility_member = fields.Many2one('members.responsibility', track_visibility='onchange')
   transfer_responsibility_leader = fields.Many2one('leaders.responsibility', track_visibility='onchange')
   transfer_membership_org = fields.Many2one('membership.organization', track_visibility='onchange')
   transfer_league_organization = fields.Many2one('membership.organization', track_visibility='onchange')
   transfer_subcity_id = fields.Many2one('membership.handlers.parent', track_visibility='onchange')
   transfer_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', transfer_subcity_id)]", store=True, track_visibility='onchange')
   transfer_main_office = fields.Many2one('main.office', domain="['&', '&', ('member_main_type_id','=', transfer_membership_org), ('wereda_id', '=', transfer_wereda_id), '|', ('for_which_members', '=', transfer_as_a_league_or_member), ('for_which_members', '=', transfer_as_a_leader_or_member)]", track_visibility='onchange', string="Transfer Basic Organization")
   transfer_member_cells = fields.Many2one('member.cells', domain="['|', '&', ('is_mixed', '=', True), ('main_office', '=', transfer_main_office), '&', ('is_mixed', '=', False), ('main_office', '=', transfer_main_office)]", track_visibility='onchange')
   transfer_league_main_office = fields.Many2one('main.office', domain="['&', '&', ('member_main_type_id', '=', transfer_league_organization), ('wereda_id', '=', transfer_wereda_id), '|', ('for_which_members', '=', transfer_as_a_league_or_member), ('for_which_members', '=', transfer_as_a_leader_or_member)]", track_visibility='onchange', string="Transfer League Basic Organization")
   transfer_league_member_cells = fields.Many2one('member.cells', domain="['|', '&', ('is_mixed', '=', True), ('main_office', '=', transfer_league_main_office), '&', ('is_mixed', '=', False), ('main_office', '=', transfer_league_main_office)]", track_visibility='onchange')
   state = fields.Selection(selection=[('draft', 'Draft'), ('review', 'Review'), ('waiting for approval', 'Waiting For Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], track_visibility='onchange', default="draft")
   responsibility_state = fields.Selection(selection=[('transfer', 'Transfer'), ('demote', 'Demote'), ('promote', 'Promote')], default='transfer', track_visibility='onchange', readonly=True)
   receiving_manager = fields.Many2one('res.users', store=True, string="Receiving Leader")
   x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
   attachment_amount = fields.Integer(compute="_count_attachments")
   for_woreda = fields.Boolean(default=False)
   for_subcity = fields.Boolean(default=False)
   for_city = fields.Boolean(default=False)
   for_main = fields.Boolean(default=False)
   for_cell = fields.Boolean(default=False)



   @api.model
   def create(self, vals):
      """This function will create a new state"""
      vals['name'] = self.env['ir.sequence'].next_by_code('members.transfer')
      return super(Transfer, self).create(vals)


   def unlink(self):
      """This function shouldn't be available for transfer"""
      for record in self:
            raise UserError(_("Transfer Documents Are Not To Be Deleted"))
      return super(Transfer, self).unlink()


   def deactivate_activity(self, record):
      """This function will deactivate an activity"""
      model = self.env['ir.model'].search([('model', '=', 'members.transfer'), ('is_mail_activity', '=', True)])
      activity_type = self.env['mail.activity.type'].search([('name', '=', 'Member Transfer')], limit=1)
      activity = self.env['mail.activity'].search([('res_id', '=', record.id), ('res_model_id', '=', model.id), ('activity_type_id', '=', activity_type.id)])
      activity.unlink()

   @api.onchange('transfer_as_a_leader_or_member')
   def _transfer_as_a_leader_or_member_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_as_a_leader_or_member == 'league' or record.transfer_as_a_leader_or_member == 'member' or record.transfer_as_a_leader_or_member == 'leader':
            record.transfer_subcity_id = False
            record.transfer_wereda_id = False
            record.transfer_main_office = False
            record.transfer_member_cells = False
            record.transfer_league_main_office = False
            record.transfer_league_member_cells = False
            record.transfer_league_responsibility = False
            record.transfer_responsibility_member = False
            record.transfer_responsibility_leader = False
            record.transfer_membership_org = False
            record.transfer_league_organization = False

   @api.onchange('transfer_as_a_league_or_member')
   def _transfer_as_a_league_or_member_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_as_a_league_or_member == 'league' or record.transfer_as_a_league_or_member == 'member':
            record.transfer_subcity_id = False
            record.transfer_wereda_id = False
            record.transfer_main_office = False
            record.transfer_member_cells = False
            record.transfer_league_main_office = False
            record.transfer_league_member_cells = False
            record.transfer_league_responsibility = False
            record.transfer_responsibility_member = False
            record.transfer_responsibility_leader = False
            record.transfer_membership_org = False
            record.transfer_league_organization = False


   @api.onchange('transfer_membership_org')
   def _member_organization_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_membership_org:
            record.transfer_subcity_id = False
            record.transfer_wereda_id = False
            record.transfer_main_office = False
            record.transfer_member_cells = False
            record.transfer_league_main_office = False
            record.transfer_league_member_cells = False


   @api.onchange('transfer_league_organization')
   def _league_organization_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_league_organization:
            record.transfer_subcity_id = False
            record.transfer_wereda_id = False
            record.transfer_main_office = False
            record.transfer_member_cells = False
            record.transfer_league_main_office = False
            record.transfer_league_member_cells = False

   @api.onchange('transfer_responsibility_leader')
   def _leader_responsibility_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_responsibility_leader:
            print(record.transfer_responsibility_leader.id)
            if record.transfer_responsibility_leader.id == 1:
               record.for_woreda = True
               record.for_subcity = False
               record.for_city = False
            if record.transfer_responsibility_leader.id == 2:
               record.for_woreda = False
               record.for_subcity = True
               record.for_city = False
            if record.transfer_responsibility_leader.id == 3:
               record.for_woreda = False
               record.for_subcity = False
               record.for_city = True

   @api.onchange('transfer_responsibility_member')
   def _member_responsibility_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_responsibility_member:
            if record.transfer_responsibility_member.id == 1:
               record.for_cell = True
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False
            if record.transfer_responsibility_member.id == 2:
               record.for_cell = True
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False
            if record.transfer_responsibility_member.id == 3:
               record.for_cell = False
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False


   @api.onchange('transfer_league_responsibility')
   def _league_responsibility_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_league_responsibility:
            if record.transfer_league_responsibility.id == 1:
               record.for_cell = True
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False
            if record.transfer_league_responsibility.id == 2:
               record.for_cell = True
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False
            if record.transfer_league_responsibility.id == 3:
               record.for_cell = False
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False

   def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
         if (record.state == 'approved' or record.state == 'rejected' or record.state == 'review' or record.state == 'waiting for approval'):
               record.x_css = '<style> .o_form_button_edit {display:None}</style>'
         else:
               record.x_css = False


   def _count_attachments(self):
      """This function will count the attchments"""
      for record in self:
         attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
         if attachments:
               record.attachment_amount = len(attachments.mapped('type'))
         else:
               record.attachment_amount = 0

   def review(self):
      """This button will start review"""
      for record in self:
         if record.receiving_manager.id == self.env.user.id:
            record.correct_user = True
         else:
            if record.receiving_manager:
               raise ValidationError(_("%s is the only person allowed to review this.") % (str(record.receiving_manager.name)))
            else:
               raise ValidationError(_("This Transfer Request Doesn't Have a Receiving Leader"))
         mail_temp = self.env.ref('transfer_waiting')
         mail_temp.send_mail(record.id)
         record.state = 'review'


   def reject_transfer(self):
      """This function will reject the new partner"""
      for record in self:
         record.wereda_id = record.from_wereda_id.id
         mail_temp = self.env.ref('transfer_rejected')
         mail_temp.send_mail(record.id)
         record.state = 'rejected'
         self.deactivate_activity(record)
         