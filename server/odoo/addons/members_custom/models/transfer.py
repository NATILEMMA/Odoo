"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta



class Transfer(models.Model):
   _name="members.transfer"
   _description="This model will create tranfer sheets for leaders "
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_wereda(self):
      """This function will set a default value to wereda"""
      return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

   name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
   wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
   wereda_manager_id = fields.Many2one('res.users', related="wereda_id.branch_manager", store=True)
   correct_user = fields.Boolean(default=False)
   partner_id = fields.Many2one('res.partner', domain="[('wereda_id', '=', wereda_id)]", track_visibility='onchange')
   is_league = fields.Boolean(related="partner_id.is_league", store=True)
   is_member = fields.Boolean(related="partner_id.is_member", store=True)
   is_leader = fields.Boolean(related="partner_id.is_leader", store=True)
   transfer_as_a_league_or_member = fields.Selection(selection=[('league', 'League'), ('member', 'Member')], track_visibility='onchange')
   transfer_as_a_leader_or_member = fields.Selection(selection=[('leader', 'Leader'), ('member', 'Member'), ('league', 'League')], track_visibility='onchange')
   from_subcity_id = fields.Many2one('membership.handlers.parent', store=True, readonly=True)
   from_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', transfer_subcity_id)]", store=True, readonly=True)
   from_main_office = fields.Many2one('main.office', readonly=True, store=True)
   from_member_cells = fields.Many2one('member.cells', readonly=True, store=True) 
   from_league_main_office = fields.Many2one('main.office', readonly=True, store=True)
   from_league_member_cells = fields.Many2one('member.cells', readonly=True, store=True)   
   leadership_experience = fields.Char(translate=True, readonly=True, store=True)
   place_of_work = fields.Char(store=True, translate=True, readonly=True)
   responsibility_in_gov = fields.Char(related="partner_id.gov_responsibility", store=True)
   league_responsibility_in_org = fields.Many2one('league.responsibility', readonly=True, store=True)
   # responsibility_in_org_league = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], default='league member', track_visibility='onchange')
   responsibility_in_org_member = fields.Many2one('members.responsibility', store=True, readonly=True)
   responsibility_in_org_leader = fields.Many2one('leaders.responsibility', readonly=True, store=True)
   league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], readonly=True, store=True)
   membership_org = fields.Many2one('membership.organization', readonly=True, store=True)
   key_strength = fields.Many2many('interpersonal.skills', 'skill_tranfer_rel', string="Strength", readonly=True, store=True)
   key_weakness = fields.Many2many('interpersonal.skills', readonly=True, store=True)
   grade = fields.Selection(related="partner_id.grade", store=True)
   leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], store=True, readonly=True)
   membership_status = fields.Char(default="Full Member", readonly=True)
   membership_fee = fields.Float(readonly=True, store=True)
   league_fee = fields.Float(readonly=True, store=True)
   transfer_league_responsibility = fields.Many2one('league.responsibility', track_visibility='onchange')
   # transfer_responsibility_league = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], default='league member', track_visibility='onchange')
   transfer_responsibility_member = fields.Many2one('members.responsibility', track_visibility='onchange')
   transfer_responsibility_leader = fields.Many2one('leaders.responsibility', track_visibility='onchange')
   transfer_membership_org = fields.Many2one('membership.organization', track_visibility='onchange')
   transfer_league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange')
   transfer_subcity_id = fields.Many2one('membership.handlers.parent', track_visibility='onchange')
   transfer_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', transfer_subcity_id)]", store=True, track_visibility='onchange')
   transfer_main_office = fields.Many2one('main.office', domain="['&', ('member_main_type_id','=', transfer_membership_org), ('wereda_id', '=', transfer_wereda_id)]", track_visibility='onchange')
   transfer_member_cells = fields.Many2one('member.cells', domain="[('main_office', '=', transfer_main_office)]", track_visibility='onchange')
   transfer_league_main_office = fields.Many2one('main.office', domain="['&', ('league_main_type_id', '=', transfer_league_org), ('wereda_id', '=', transfer_wereda_id)]", track_visibility='onchange')
   transfer_league_member_cells = fields.Many2one('member.cells', domain="[('main_office_league', '=', transfer_league_main_office)]", track_visibility='onchange')
   state = fields.Selection(selection=[('draft', 'draft'), ('review', 'Review'), ('waiting for approval', 'Waiting For Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], track_visibility='onchange')
   responsibility_state = fields.Selection(selection=[('transfer', 'Transfer'), ('demote', 'Demote'), ('promote', 'Promote')], default='transfer', track_visibility='onchange')
   receiving_manager = fields.Many2one('res.users', readonly=True, store=True)
   x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
   for_woreda = fields.Boolean(default=False)
   for_subcity = fields.Boolean(default=False)
   for_city = fields.Boolean(default=False)
   for_main = fields.Boolean(default=False)
   for_cell = fields.Boolean(default=False)



   @api.model
   def create(self, vals):
      """This function will create a new state"""
      vals['name'] = self.env['ir.sequence'].next_by_code('members.transfer')
      transfers = self.env['members.transfer'].search([('partner_id', '=', vals['partner_id']), ('state', 'in', ('draft', 'review', 'waiting for approval'))])
      if len(transfers.ids) > 0:
         raise ValidationError(_("This Person Has A Transfer That Hasn't Been Reviewed Yet. Please Wait Until A Decision Has Been Made"))
      vals['state'] = 'draft'
      rec = super(Transfer, self).create(vals)
      if rec.partner_id and rec.transfer_as_a_league_or_member == 'member' and rec.is_league == True and rec.is_member == False and rec.is_leader == False:
         raise ValidationError(_('Only Those Leagues Who Are Also Full Members are allowed to transfer as Members'))
      if rec.partner_id and rec.transfer_as_a_leader_or_member == 'league' and rec.is_league == False:
         raise ValidationError(_('Only Those Leaders Who Are Also Leagues are allowed to transfer as Leagues'))
      if rec.partner_id and rec.transfer_as_a_league_or_member == 'league' and rec.is_league == False:
         raise ValidationError(_('Only Those Members Who Are Also Leagues are allowed to transfer as Leagues'))
      if (rec.is_league == True and rec.transfer_as_a_league_or_member == '') or (rec.is_member == True and rec.transfer_as_a_league_or_member == '') or (rec.is_leader == True and rec.transfer_as_a_leader_or_member == ''):
         raise ValidationError(_('What would you like to be transfered as?'))
      if rec.transfer_as_a_leader_or_member == 'leader':
         rec.receiving_manager = rec.from_subcity_id.city_id.transfer_handler.id
      if (not rec.transfer_main_office and not rec.transfer_member_cells) or (not rec.transfer_league_main_office and not rec.transfer_league_member_cells):
         rec.receiving_manager = rec.transfer_wereda_id.branch_manager.id
      return rec

   def unlink(self):
      """This function shouldn't be available for transfer"""
      for record in self:
         if record.state != 'draft':
            raise UserError(_("Transfer Documents Are Not To Be Deleted"))
      return super(Transfer, self).unlink()


   @api.onchange('transfer_responsibility_leader')
   def _leader_responsibility_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_responsibility_leader:
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
            if record.transfer_league_responsibility.id == 31:
               record.for_cell = True
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False
            if record.transfer_league_responsibility.id == 32:
               record.for_cell = True
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False
            if record.transfer_league_responsibility.id == 33:
               record.for_cell = False
               record.for_main = True
               record.for_woreda = True
               record.for_subcity = True
               record.for_city = False

   def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
         if self.env.user.has_group('members_custom.member_group_manager') and (record.state == 'approved' or record.state == 'rejected' or record.state == 'review'):
               record.x_css = '<style> .o_form_button_edit {display:None}</style>'
         else:
               record.x_css = False

   def add_attachment(self):
      """This function will add attachments"""
      for record in self:
         wizard = self.env['attachment.wizard'].create({
               'res_id': record.partner_id.id,
               'res_model': 'res.partner'
         })
         return {
               'name': _('Create Attachment Wizard'),
               'type': 'ir.actions.act_window',
               'res_model': 'attachment.wizard',
               'view_mode': 'form',
               'res_id': wizard.id,
               'target': 'new'
         }

   def review(self):
      """This button will start review"""
      for record in self:
         # if record.receiving_manager_city.id == self.env.user.id:
         #    record.correct_user = True   
         # else:
         #    message = "The Transfer Handler for the city " + str(record.from_subcity_id.city_id.name) + " is the only person allowed to review this."
         #    raise ValidationError(_(message))
         if record.receiving_manager.id == self.env.user.id:
            record.correct_user = True
         else:
            message = "The manager for the Woreda " + str(record.transfer_wereda_id.name) + " is the only person allowed to review this."
            raise ValidationError(_(message))
         mail_temp = self.env.ref('members_custom.transfer_waiting')
         mail_temp.send_mail(record.id)
         record.state = 'review'

   def waiting_for_approval(self):
      """This function will send the tranfer to the requested person"""
      for record in self:
      #    record.wereda_id = record.transfer_wereda_id.id
      #    if record.wereda_manager_id.id == self.env.user.id:
      #       record.correct_user = True
         record.state = 'waiting for approval'

   # @api.onchange('transfer_as_a_league_or_member')
   # def _not_member_no_transfer(self):
   #    """This function will not allow just leagues to transfer as members"""
   #    for record in self:
   #       if record.partner_id and record.transfer_as_a_league_or_member == 'member' and (record.is_member == False or record.is_leader == False):
   #          raise UserError(_('Only Those Leagues Who Are Also Full Members are allowed to transfer as Members'))


   def approve_transfer(self):
      """This function will approve the new partner"""
      for record in self:
         if record.is_leader:
            if record.transfer_as_a_leader_or_member == 'leader':
               if record.transfer_responsibility_leader.id == 1:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('members_custom.member_group_manager').id])]
                  })
                  message = str(user.name) + " Has Been Approved To Become The Manager For " + str(record.transfer_wereda_id.name) + ". Please Make The Right Adjustments for The Promoted and Removed Personnel."
                  model = self.env['ir.model'].search([('model', '=', 'membership.handlers.branch'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'Woreda Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Woreda Manager Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.transfer_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.transfer_wereda_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.transfer_subcity_id.city_id.transfer_handler.notify_warning(message, '<h4>Woreda Manager Transfer</h4>', True)

               if record.transfer_responsibility_leader.id == 2:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('members_custom.member_group_admin').id])]
                  })
                  message = str(user.name) + " Has Been Approved To Become The Manager For " + str(record.transfer_subcity_id.name) + ". Please Make The Right Adjustments for The Promoted and Removed Personnel."
                  model = self.env['ir.model'].search([('model', '=', 'membership.handlers.parent'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'Subcity Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Subcity Manager Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.transfer_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.transfer_subcity_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.transfer_subcity_id.city_id.transfer_handler.notify_warning(message, '<h4>Subcity Manager Transfer</h4>', True)

               if record.transfer_responsibility_leader.id == 3:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('members_custom.member_group_city_admin').id])]
                  })
                  message = str(user.name) + " Has Been Approved To Become The Manager For " + str(record.from_subcity_id.city_id.name) + ". Please Make The Right Adjustments for The Promoted and Removed Personnel."
                  model = self.env['ir.model'].search([('model', '=', 'membership.city.handlers'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'City Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "City Manager Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.from_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.from_subcity_id.city_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.from_subcity_id.city_id.transfer_handler.notify_warning(message, '<h4>City Manager Transfer</h4>', True)
               record.partner_id.leader_responsibility = record.transfer_responsibility_leader.id

            if record.transfer_as_a_leader_or_member == 'member':
               if record.transfer_member_cells:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,
                     'main_office': record.transfer_main_office.id,
                     'member_cells': record.transfer_member_cells.id
                  }) 
               else:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,
                     'main_office': False,
                     'member_cells': False
                  })

               if record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 1:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  record.responsibility_state = 'transfer' 

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 2):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]  
                  record.responsibility_state = 'promote' 

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 3):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  record.responsibility_state = 'promote' 

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 2:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]  
                  record.responsibility_state = 'transfer' 

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 3):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  record.responsibility_state = 'promote' 

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 1):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.responsibility_state = 'demote' 

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 3:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))] 
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members_cell = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members_cell)]  
                  all_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_members)] 
                  record.responsibility_state = 'transfer'

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 2):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]
                  record.responsibility_state = 'demote'

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 1):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.responsibility_state = 'demote'

            if record.transfer_as_a_leader_or_member == 'league':
               if record.transfer_league_member_cells:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,                  
                     'league_main_office': record.transfer_league_main_office.id,
                     'league_member_cells': record.transfer_league_member_cells.id
                  })
               else:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,                  
                     'league_main_office': False,
                     'league_member_cells': False
                  })

               if record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 31:
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               elif (record.league_responsibility_in_org.id == 31) and (record.transfer_league_responsibility.id == 32):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'promote' 

               elif (record.league_responsibility_in_org.id == 31) and (record.transfer_league_responsibility.id == 33):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]  
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'promote' 


               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 32:
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               elif (record.league_responsibility_in_org.id == 32) and (record.transfer_league_responsibility.id == 33):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee 
                  all_cell_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_cell_leagues)]  
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'promote' 

               elif (record.league_responsibility_in_org.id == 32) and (record.transfer_league_responsibility.id == 31):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'demote' 

               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 33:
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]                    
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               elif (record.league_responsibility_in_org.id == 33) and (record.transfer_league_responsibility.id == 32):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
                  record.responsibility_state = 'demote' 

               elif (record.league_responsibility_in_org.id == 33) and (record.transfer_league_responsibility.id == 31):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'demote' 

         else:            

            if record.transfer_as_a_league_or_member == 'league':
               if record.transfer_league_member_cells:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,                  
                     'league_main_office': record.transfer_league_main_office.id,
                     'league_member_cells': record.transfer_league_member_cells.id
                  })
               else:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,                  
                     'league_main_office': False,
                     'league_member_cells': False
                  })

               if record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 31:
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               elif (record.league_responsibility_in_org.id == 31) and (record.transfer_league_responsibility.id == 32):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'promote' 

               elif (record.league_responsibility_in_org.id == 31) and (record.transfer_league_responsibility.id == 33):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]  
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'promote' 


               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 32:
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               elif (record.league_responsibility_in_org.id == 32) and (record.transfer_league_responsibility.id == 33):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee 
                  all_cell_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_cell_leagues)]  
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'promote' 

               elif (record.league_responsibility_in_org.id == 32) and (record.transfer_league_responsibility.id == 31):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'demote' 

               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 33:
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]                    
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               elif (record.league_responsibility_in_org.id == 33) and (record.transfer_league_responsibility.id == 32):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
                  record.responsibility_state = 'demote' 

               elif (record.league_responsibility_in_org.id == 33) and (record.transfer_league_responsibility.id == 31):
                  record.partner_id.league_org = record.transfer_league_org
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'demote'                


            if record.transfer_as_a_league_or_member == 'member':
               if record.transfer_member_cells:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,
                     'main_office': record.transfer_main_office.id,
                     'member_cells': record.transfer_member_cells.id
                  }) 
               else:
                  record.partner_id.write({
                     'subcity_id': record.transfer_subcity_id.id,
                     'wereda_id': record.transfer_wereda_id.id,
                     'main_office': False,
                     'member_cells': False
                  }) 

               if record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 1:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  record.responsibility_state = 'transfer' 

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 2):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]  
                  record.responsibility_state = 'promote' 

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 3):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  record.responsibility_state = 'promote' 

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 2:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]  
                  record.responsibility_state = 'transfer' 

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 3):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  record.responsibility_state = 'promote' 

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 1):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.responsibility_state = 'demote' 

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 3:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))] 
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members_cell = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members_cell)]  
                  all_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_members)] 
                  record.responsibility_state = 'transfer'

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 2):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]
                  record.responsibility_state = 'demote'

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 1):
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.responsibility_state = 'demote'

         mail_temp = self.env.ref('members_custom.transfer_approved')
         mail_temp.send_mail(record.id)
         record.state = 'approved'


   def reject_transfer(self):
      """This function will reject the new partner"""
      for record in self:
         record.wereda_id = record.from_wereda_id.id
         mail_temp = self.env.ref('members_custom.transfer_rejected')
         mail_temp.send_mail(record.id)
         record.state = 'rejected'
         

   @api.onchange('partner_id', 'transfer_as_a_league_or_member', 'transfer_as_a_leader_or_member')
   def _populate_the_missing_fields(self):
      """This function will populate the missing fields from res partner"""
      for record in self:
         if record.partner_id:
            current_job = record.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
            if current_job:
               record.place_of_work = current_job.place_of_work
            else:
               record.place_of_work = ''
            record.key_strength = record.partner_id.key_strength.ids
            record.key_weakness = record.partner_id.key_weakness.ids
            record.from_subcity_id = record.partner_id.subcity_id.id
            record.from_wereda_id = record.partner_id.wereda_id.id
            if record.partner_id.is_league == True:
               record.league_org = record.partner_id.league_org
               record.league_responsibility_in_org = record.partner_id.league_responsibility.id
               record.league_fee = record.partner_id.league_payment 
               record.from_league_main_office = record.partner_id.league_main_office.id
               record.from_league_member_cells = record.partner_id.league_member_cells.id

            if record.partner_id.is_leader == True:
               record.leadership_experience = record.partner_id.experience
               record.responsibility_in_org_leader = record.partner_id.leader_responsibility.id
               record.membership_fee = record.partner_id.membership_monthly_fee_cash + record.partner_id.membership_monthly_fee_cash_from_percent
               record.leadership_status = record.partner_id.leadership_status
               record.membership_org = record.partner_id.membership_org.id
               record.from_main_office = record.partner_id.main_office.id
               record.from_member_cells = record.partner_id.member_cells.id

            if record.partner_id.is_member == True:
               record.membership_org = record.partner_id.membership_org.id
               record.responsibility_in_org_member = record.partner_id.member_responsibility.id
               record.membership_fee = record.partner_id.membership_monthly_fee_cash + record.partner_id.membership_monthly_fee_cash_from_percent
               record.from_main_office = record.partner_id.main_office.id
               record.from_member_cells = record.partner_id.member_cells.id