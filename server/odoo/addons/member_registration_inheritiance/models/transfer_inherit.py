"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta



class Transfer(models.Model):
   _inherit="members.transfer"

   partner_id = fields.Many2one('res.partner', track_visibility='onchange', domain="['&', '|', '|', ('is_league', '=', True), ('is_member', '=', True), ('is_leader', '=', True), '&', '|', ('member_cells', '!=', False), ('league_member_cells', '!=', False), '|', '|', '|', '|', '|', '|', ('subcity_id.city_id', '=', city_id), ('subcity_id', '=', subcity_id), ('wereda_id', '=', wereda_id), ('main_office', '=', main_office_id), ('league_main_office', '=', main_office_id), ('member_cells', '=', cell_id), ('league_member_cells', '=', cell_id)]")
   is_league = fields.Boolean(related="partner_id.is_league", store=True)
   is_member = fields.Boolean(related="partner_id.is_member", store=True)
   is_leader = fields.Boolean(related="partner_id.is_leader", store=True)
   transfer_as_a_league_or_member = fields.Selection(selection=[('league', 'League'), ('member', 'Member')], track_visibility='onchange')
   transfer_as_a_leader_or_member = fields.Selection(selection=[('leader', 'Leader'), ('member', 'Member'), ('league', 'League')], track_visibility='onchange')
   from_subcity_id = fields.Many2one('membership.handlers.parent', store=True, compute="_populate_the_missing_fields")
   from_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', transfer_subcity_id)]", store=True, compute="_populate_the_missing_fields")
   from_main_office = fields.Many2one('main.office', compute="_populate_the_missing_fields", store=True, string="From Basic Organization")
   from_member_cells = fields.Many2one('member.cells', compute="_populate_the_missing_fields", store=True) 
   from_league_main_office = fields.Many2one('main.office', compute="_populate_the_missing_fields", store=True, string="From League Basic Organization")
   from_league_member_cells = fields.Many2one('member.cells', compute="_populate_the_missing_fields", store=True)   
   leadership_experience = fields.Char(translate=True, compute="_populate_the_missing_fields", store=True)
   place_of_work = fields.Char(store=True, translate=True, compute="_populate_the_missing_fields")
   responsibility_in_gov = fields.Char(compute="_populate_the_missing_fields", store=True)
   league_responsibility_in_org = fields.Many2one('league.responsibility', compute="_populate_the_missing_fields", store=True)
   responsibility_in_org_member = fields.Many2one('members.responsibility', store=True, compute="_populate_the_missing_fields")
   responsibility_in_org_leader = fields.Many2one('leaders.responsibility', compute="_populate_the_missing_fields", store=True)
   league_organization = fields.Many2one('membership.organization', compute="_populate_the_missing_fields", store=True)
   membership_org = fields.Many2one('membership.organization', compute="_populate_the_missing_fields", store=True)
   key_strength = fields.Many2many('interpersonal.skills', 'skill_tranfer_rel', string="Strength", compute="_populate_the_missing_fields", store=True)
   key_weakness = fields.Many2many('interpersonal.skills', compute="_populate_the_missing_fields", store=True)
   grade = fields.Char(store=True, compute="_populate_the_missing_fields")
   leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], store=True, compute="_populate_the_missing_fields")
   membership_fee = fields.Float(compute="_populate_the_missing_fields", store=True)
   league_fee = fields.Float(compute="_populate_the_missing_fields", store=True)



   @api.model
   def create(self, vals):
      """This function will create a new state"""
      transfers = self.env['members.transfer'].search([('partner_id', '=', vals['partner_id']), ('state', 'in', ('draft', 'review', 'waiting for approval'))])
      if len(transfers.ids) > 0:
         raise ValidationError(_("This Person Has A Transfer That Hasn't Been Reviewed Yet. Please Wait Until A Decision Has Been Made"))
      rec =  super(Transfer, self).create(vals)
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
      if rec.transfer_league_member_cells and not rec.transfer_member_cells:
         rec.receiving_manager = rec.transfer_league_member_cells.cell_admin.id
      if not rec.transfer_league_member_cells and rec.transfer_member_cells:
         rec.receiving_manager = rec.transfer_member_cells.cell_admin.id
      if rec.transfer_responsibility_leader:
         if rec.transfer_responsibility_leader.id == 1:
            rec.for_woreda = True
            rec.for_subcity = False
            rec.for_city = False
         if rec.transfer_responsibility_leader.id == 2:
            rec.for_woreda = False
            rec.for_subcity = True
            rec.for_city = False
         if rec.transfer_responsibility_leader.id == 3:
            rec.for_woreda = False
            rec.for_subcity = False
            rec.for_city = True
      return rec


   def waiting_for_approval(self):
      """This function will send the tranfer to the requested person"""
      for record in self:
         if record.attachment_amount == 0:
            raise UserError(_("Please Attach Transfer Documents"))
         message = _("%s's Transfer Has Been Sent To You For Reviewing") % (str(record.partner_id.name))
         title = _("<h4>Transfer Review</h4>")
         model = self.env['ir.model'].search([('model', '=', 'members.transfer'), ('is_mail_activity', '=', True)])
         activity_type = self.env['mail.activity.type'].search([('name', '=', 'Member Transfer')], limit=1)
         self.env['mail.activity'].sudo().create({
               'display_name': message,
               'summary': "Member Transfer",
               'date_deadline': date.today() + relativedelta(month=1),
               'user_id': record.receiving_manager.id,
               'res_model_id': model.id,
               'res_id': record.id,
               'activity_type_id': activity_type.id
         })
         record.receiving_manager.notify_warning(message, title, True)
         record.state = 'waiting for approval'


   def approve_transfer(self):
      """This function will approve the new partner"""
      for record in self:
         if record.is_leader:
            if record.transfer_as_a_leader_or_member == 'leader':
               if record.transfer_responsibility_leader.id == 1:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_manager').id])]
                  })
                  message = _("%s Has Been Approved To Become The Leader For %s. Please Make The Right Adjustments for The Promoted and Removed Personnel.") % (str(user.name), str(record.transfer_wereda_id.name))
                  title = _("<h4>Woreda Leader Transfer</h4>")
                  model = self.env['ir.model'].search([('model', '=', 'membership.handlers.branch'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'Woreda Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Woreda Leader Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.transfer_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.transfer_wereda_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.transfer_wereda_id.make_readonly = False
                  record.transfer_subcity_id.city_id.transfer_handler.notify_warning(message, title, True)

               if record.transfer_responsibility_leader.id == 2:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_admin').id])]
                  })
                  message = _("%s Has Been Approved To Become The Leader For %s. Please Make The Right Adjustments for The Promoted and Removed Personnel.") % (str(user.name), str(record.transfer_subcity_id.name))
                  title = _("<h4>Subcity Leader Transfer</h4>")
                  model = self.env['ir.model'].search([('model', '=', 'membership.handlers.parent'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'Subcity Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Subcity LeaderTransfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.transfer_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.transfer_subcity_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.transfer_subcity_id.make_readonly = False
                  record.transfer_subcity_id.city_id.transfer_handler.notify_warning(message, title, True)

               if record.transfer_responsibility_leader.id == 3:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_city_admin').id])]
                  })
                  message = _("%s Has Been Approved To Become The Leader For %s. Please Make The Right Adjustments for The Promoted and Removed Personnel.") % (str(user.name), str(record.from_subcity_id.city_id.name))
                  title =_("<h4>City Leader Transfer</h4>")
                  model = self.env['ir.model'].search([('model', '=', 'membership.city.handlers'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'City Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "City Leader Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.from_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.from_subcity_id.city_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.from_subcity_id.city_id.make_readonly = False
                  record.from_subcity_id.city_id.transfer_handler.notify_warning(message, title, True)
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

               # Working

               if record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 1:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)]
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids_mixed = [(6, 0, all_members)]
                  record.transfer_member_cells.cell_admin = user.id 
                  record.responsibility_state = 'promote' 


               # Working               

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 3):
                  raise UserError(_("You Need To Be Transfered to Cell Leader first"))
                  # record.partner_id.membership_org = record.transfer_membership_org.id
                  # record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  # record.from_main_office.total_members -= 1
                  # record.from_main_office.total_membership_fee -= record.membership_fee
                  # record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  # record.transfer_main_office.total_members += 1
                  # record.transfer_main_office.total_membership_fee += record.membership_fee
                  # all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  # record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  # record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  # all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  # record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  # record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  # record.responsibility_state = 'promote' 

               # Working

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 2:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_member_cells.cell_admin = False
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]  
                  record.transfer_member_cells.leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids_mixed = [(6, 0, all_members)]  
                  record.transfer_member_cells.cell_admin = user.id
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 3):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_main_manager').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_member_cells.cell_admin = False
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)] 
                  all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  record.transfer_main_office.main_admin = user.id
                  record.responsibility_state = 'promote' 

               # Working

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_member_cells.cell_admin = False
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)]
                  record.responsibility_state = 'demote' 


               # Working

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 3:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))] 
                  record.from_main_office.main_admin = False
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members_cell = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members_cell)]  
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members_cell)]  
                  all_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_members)] 
                  record.transfer_main_office.main_admin = user.id
                  record.responsibility_state = 'transfer'

               # Working

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_main_office.main_admin = False
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids_mixed = [(6, 0, all_members)]
                  record.transfer_member_cells.cell_admin = user.id
                  record.responsibility_state = 'demote'

               # Working

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_main_office.main_admin = False
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)]
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

               # Working

               if record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 1:
                  
                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.league_responsibility_in_org.id == 1) and (record.transfer_league_responsibility.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.cell_admin = user.id
                  record.responsibility_state = 'promote' 

                # Working

               elif (record.league_responsibility_in_org.id == 1) and (record.transfer_league_responsibility.id == 3):

                  raise UserError(_("You Need To Be Transfered to Cell Leader first"))

                  # user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  # if user:
                  #    user.write({
                  #       'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_main_manager').id])]
                  #    })

                  # record.partner_id.league_organization = record.transfer_league_organization.id
                  # record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  # record.from_league_main_office.total_leagues -= 1
                  # record.from_league_main_office.total_leagues_fee -= record.league_fee
                  # record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  # record.transfer_league_main_office.total_leagues += 1
                  # record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  # all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  # record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  # record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]  
                  # all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  # record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  # record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  # record.transfer_league_main_office.main_admin = user.id
                  # record.responsibility_state = 'promote' 

               # Working

               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 2:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])    

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.league_leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.cell_admin = False
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]  
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(6, 0, all_leagues)] 
                  record.transfer_league_member_cells.cell_admin = user.id
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.league_responsibility_in_org.id == 2) and (record.transfer_league_responsibility.id == 3):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_main_manager').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.league_leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.cell_admin = False
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee 
                  all_cell_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_cell_leagues)]  
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_cell_leagues)] 
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.transfer_league_main_office.main_admin = user.id
                  record.responsibility_state = 'promote' 

               # Working

               elif (record.league_responsibility_in_org.id == 2) and (record.transfer_league_responsibility.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.league_leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.cell_admin = False
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_leagues)]
                  record.responsibility_state = 'demote' 

               # Working

               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 3:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.main_admin = False
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]     
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_league_cell)]                
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]
                  record.transfer_league_main_office.main_admin = user.id

                  record.responsibility_state = 'transfer' 

                # Working

               elif (record.league_responsibility_in_org.id == 3) and (record.transfer_league_responsibility.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_main_office.main_admin = False
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.cell_admin = user.id

                  record.responsibility_state = 'demote' 

               # Working

               elif (record.league_responsibility_in_org.id == 3) and (record.transfer_league_responsibility.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_main_office.main_admin = False
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_leagues)]
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

               # Working

               if record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 1:
                  
                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]  
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_leagues)]  
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.league_responsibility_in_org.id == 1) and (record.transfer_league_responsibility.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.cell_admin = user.id
                  record.responsibility_state = 'promote' 

                # Working

               elif (record.league_responsibility_in_org.id == 1) and (record.transfer_league_responsibility.id == 3):

                  raise UserError(_("You Need To Be Transfered to Cell Leader first"))

                  # user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  # if user:
                  #    user.write({
                  #       'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_main_manager').id])]
                  #    })

                  # record.partner_id.league_organization = record.transfer_league_organization.id
                  # record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  # record.from_league_main_office.total_leagues -= 1
                  # record.from_league_main_office.total_leagues_fee -= record.league_fee
                  # record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  # record.transfer_league_main_office.total_leagues += 1
                  # record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  # all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  # record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  # record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]  
                  # all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  # record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  # record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  # record.transfer_league_main_office.main_admin = user.id
                  # record.responsibility_state = 'promote' 

               # Working

               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 2:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])    

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.league_leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.cell_admin = False
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]  
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(6, 0, all_leagues)] 
                  record.transfer_league_member_cells.cell_admin = user.id
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.league_responsibility_in_org.id == 2) and (record.transfer_league_responsibility.id == 3):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_main_manager').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.league_leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.cell_admin = False
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee 
                  all_cell_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_cell_leagues)]  
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_cell_leagues)] 
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]  
                  record.transfer_league_main_office.main_admin = user.id
                  record.responsibility_state = 'promote' 

               # Working

               elif (record.league_responsibility_in_org.id == 2) and (record.transfer_league_responsibility.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.league_leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.cell_admin = False
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_leagues)]
                  record.responsibility_state = 'demote' 

               # Working

               elif record.league_responsibility_in_org.id == record.transfer_league_responsibility.id == 3:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.main_admin = False
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_league_cell = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_league_cell)]     
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_league_cell)]                
                  all_leagues = record.transfer_league_main_office.league_leader_ids.ids + [record.partner_id.id]
                  record.transfer_league_main_office.league_leader_ids = [(5, 0, 0)]
                  record.transfer_league_main_office.league_leader_ids = [(6, 0, all_leagues)]
                  record.transfer_league_main_office.main_admin = user.id

                  record.responsibility_state = 'transfer' 

                # Working

               elif (record.league_responsibility_in_org.id == 3) and (record.transfer_league_responsibility.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_main_office.main_admin = False
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee
                  all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.league_leaders_ids_mixed = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.cell_admin = user.id

                  record.responsibility_state = 'demote' 

               # Working

               elif (record.league_responsibility_in_org.id == 3) and (record.transfer_league_responsibility.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.league_organization = record.transfer_league_organization.id
                  record.partner_id.league_responsibility = record.transfer_league_responsibility.id
                  record.from_league_main_office.total_leagues -= 1
                  record.from_league_main_office.total_leagues_fee -= record.league_fee
                  record.from_league_main_office.league_leader_ids = [(3, int(record.partner_id.id))]
                  record.from_league_main_office.main_admin = False
                  record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
                  record.from_league_member_cells.leagues_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_league_main_office.total_leagues += 1
                  record.transfer_league_main_office.total_leagues_fee += record.league_fee  
                  all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
                  record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(5, 0, 0)]
                  record.transfer_league_member_cells.leagues_ids_mixed = [(6, 0, all_leagues)]
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

               # Working

               if record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 1:
                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)]
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids_mixed = [(6, 0, all_members)]
                  record.transfer_member_cells.cell_admin = user.id 
                  record.responsibility_state = 'promote' 


               # Working               

               elif (record.responsibility_in_org_member.id == 1) and (record.transfer_responsibility_member.id == 3):
                  raise UserError(_("You Need To Be Transfered to Cell Leader first"))
                  # record.partner_id.membership_org = record.transfer_membership_org.id
                  # record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  # record.from_main_office.total_members -= 1
                  # record.from_main_office.total_membership_fee -= record.membership_fee
                  # record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  # record.transfer_main_office.total_members += 1
                  # record.transfer_main_office.total_membership_fee += record.membership_fee
                  # all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  # record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  # record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  # all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  # record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  # record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  # record.responsibility_state = 'promote' 

               # Working

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 2:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_member_cells.cell_admin = False
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]  
                  record.transfer_member_cells.leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids_mixed = [(6, 0, all_members)]  
                  record.transfer_member_cells.cell_admin = user.id
                  record.responsibility_state = 'transfer' 

               # Working

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 3):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_main_manager').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_member_cells.cell_admin = False
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]  
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)] 
                  all_main_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_main_members)] 
                  record.transfer_main_office.main_admin = user.id
                  record.responsibility_state = 'promote' 

               # Working

               elif (record.responsibility_in_org_member.id == 2) and (record.transfer_responsibility_member.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_member_cells.leaders_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.leaders_ids_mixed = [(3, int(record.partner_id.id))]
                  record.from_member_cells.cell_admin = False
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)]
                  record.responsibility_state = 'demote' 


               # Working

               elif record.responsibility_in_org_member.id == record.transfer_responsibility_member.id == 3:

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))] 
                  record.from_main_office.main_admin = False
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members_cell = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members_cell)]  
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members_cell)]  
                  all_members = record.transfer_main_office.leader_ids.ids + [record.partner_id.id]
                  record.transfer_main_office.leader_ids = [(5, 0, 0)]
                  record.transfer_main_office.leader_ids = [(6, 0, all_members)] 
                  record.transfer_main_office.main_admin = user.id
                  record.responsibility_state = 'transfer'

               # Working

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 2):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('member_minor_configuration.member_group_cell_manager').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_main_office.main_admin = False
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.leaders_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.leaders_ids = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.leaders_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.leaders_ids_mixed = [(6, 0, all_members)]
                  record.transfer_member_cells.cell_admin = user.id
                  record.responsibility_state = 'demote'

               # Working

               elif (record.responsibility_in_org_member.id == 3) and (record.transfer_responsibility_member.id == 1):

                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  if user:
                     user.write({
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                     })

                  record.partner_id.membership_org = record.transfer_membership_org.id
                  record.partner_id.member_responsibility = record.transfer_responsibility_member.id
                  record.from_main_office.total_members -= 1
                  record.from_main_office.total_membership_fee -= record.membership_fee
                  record.from_main_office.leader_ids = [(3, int(record.partner_id.id))]
                  record.from_main_office.main_admin = False
                  record.from_member_cells.members_ids = [(3, int(record.partner_id.id))]
                  record.from_member_cells.members_ids_mixed = [(3, int(record.partner_id.id))]
                  record.transfer_main_office.total_members += 1
                  record.transfer_main_office.total_membership_fee += record.membership_fee
                  all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
                  record.transfer_member_cells.members_ids = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids = [(6, 0, all_members)]
                  record.transfer_member_cells.members_ids_mixed = [(5, 0, 0)]
                  record.transfer_member_cells.members_ids_mixed = [(6, 0, all_members)]
                  record.responsibility_state = 'demote'

         mail_temp = self.env.ref('members_features.transfer_approved')
         mail_temp.send_mail(record.id)
         record.state = 'approved'
         self.deactivate_activity(record)

         

   @api.depends('partner_id', 'transfer_as_a_league_or_member', 'transfer_as_a_leader_or_member')
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
            record.responsibility_in_gov = record.partner_id.gov_responsibility 
            record.grade = record.partner_id.grade
            if record.partner_id.is_league == True:
               record.league_organization = record.partner_id.league_organization.id
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