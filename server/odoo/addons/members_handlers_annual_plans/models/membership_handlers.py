"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta



class ResponsibleBodies(models.Model):
   _name="responsible.bodies"
   _description="This model will handle with the creation of Responsible bodies"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(translate=True, required=True, size=64)
   system_admin = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_user_admin").id)], string="System Adminstrator", required=True, track_visibility='onchange')
   responsible_for_ids = fields.One2many('membership.city.handlers', 'responsible_id', copy=False, readonly=True)


   @api.model
   def create(self, vals):
      """This will make sure there is no duplicated responsible body"""
      body = self.env['responsible.bodies'].search([])
      if body:
         raise UserError(_("You can only have one System Admin"))

      return super(ResponsibleBodies, self).create(vals)

   def unlink(self):
      """This function will deny deletion if the record has cities"""
      for record in self:
         if len(record.responsible_for_ids.ids) > 0:
            raise UserError(_("You Can Not Delete A Responsible Body That Has a City Under It."))
      return super(ResponsibleBodies, self).unlink()


class MembershipCityHandlers(models.Model):
   _name="membership.city.handlers"
   _description="City Wide Handlers"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_body(self):
      """This function will give the city default Responsible body"""
      return self.env['responsible.bodies'].search([]).id

   name = fields.Char(required=True, string="City", translate=True, copy=False, size=64)
   city_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_city_admin").id)], string="City Leader", required=True, track_visibility='onchange', store=True) 
   ict_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_city_admin").id)], string="ICT Leader", required=True, track_visibility='onchange', store=True)  
   transfer_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_city_transfer_handler").id)], string="Leaders Transfer Handlers", required=True, track_visibility='onchange')
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("member_minor_configuration.member_group_complaint_management").id)], required=True, track_visibility='onchange')
   responsible_id = fields.Many2one('responsible.bodies', default=_default_body, required=True,readonly=True)  
   subcity_ids = fields.One2many('membership.handlers.parent', 'city_id', copy=False, readonly=True, track_visibility='onchange')
   annual_plan_state = fields.Integer(compute="annual_plan_amount")
   bypass_plannig = fields.Boolean(default=False)
   subcities = fields.Boolean(default=False)
   make_readonly = fields.Boolean(default=False)
   total = fields.Integer(store=True, compute="_check_if_it_has_subcities")

   @api.model
   def create(self, vals):
      """This will make sure there is no duplicated city"""
      body = self.env['membership.city.handlers'].search([])
      if body:
         raise UserError(_("You can only have one City"))

      res = super(MembershipCityHandlers, self).create(vals)
      res.make_readonly = True
      return res

   @api.onchange('city_manager')
   def _readonly_city(self):
      """This function will make a readonly"""
      for record in self:
         if record.city_manager and self.env.user.has_group('member_minor_configuration.member_group_city_transfer_handler'):
            record.make_readonly = True

   def unlink(self):
      """This function will deny deletion if the record has subcities"""
      for record in self:
         if len(record.subcity_ids.ids) > 0:
            raise UserError(_("You Can Not Delete A City That Has a Sub City Under It."))
      return super(MembershipCityHandlers, self).unlink()

   def revise_annual_planning(self):
      """This function will make city plans state draft"""
      for record in self:
         plans = self.env['annual.plans'].search([('fiscal_year.state', '=', 'active'), ('state', '=', 'approved')])
         if plans:
            for plan in plans:
               self.env['revised.plan.history'].sudo().create({
                  'name_city': plan.id,
                  'of_city': True,
                  'type_of_member': plan.type_of_member,
                  'male': plan.male,
                  'female': plan.female,
                  'total_estimated': plan.total_estimated,
                  'fiscal_year': plan.fiscal_year.id,
                  'approved_date': plan.approved_date,
                  'revised_date': date.today(),
                  'city_id': record.id,
                  'total_estimated': plan.total_estimated
               })
               plan.state = 'draft'


   def annual_plan_amount(self):
      """This function will count the approved states"""
      for record in self:
         plans = self.env['annual.plans'].search([('fiscal_year.state', '=', 'active')]).filtered(lambda rec: rec.state == 'approved')
         record.annual_plan_state = len(plans)

   @api.depends('subcity_ids')
   def _check_if_it_has_subcities(self):
      """This function will check if the subcity has woredas"""
      for record in self:
         record.total = len(record.subcity_ids.ids)
         if record.total > 0:
            record.subcities = True
         else:
            record.subcities = False

   @api.onchange('name')
   def _validate_name(self):
      """This function will validate the name given"""
      for record in self:
         no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
         if record.name:
               for st in record.name:
                  if st.isdigit():
                     raise UserError(_("You Can't Have A Digit in City Name"))


class MembershipHandlersParent(models.Model):
   _name="membership.handlers.parent"
   _description="Subcity Handlers"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_city(self):
      """This function will add the correct city for subcities"""
      return self.env['membership.city.handlers'].search([]).id

   name = fields.Char(required=True, string="Subcity/Sector", translate=True, copy=False, track_visibility='onchange', size=64)
   parent_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_admin").id)], string="Subcity Leader", copy=False, required=True, track_visibility='onchange', store=True)
   ict_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_admin").id)], string="ICT Leader", copy=False, required=True, track_visibility='onchange', store=True)
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("member_minor_configuration.member_group_complaint_management").id)], required=True, track_visibility='onchange')   
   branch_ids = fields.One2many('membership.handlers.branch', 'parent_id', copy=False, readonly=True, track_visibility='onchange')
   city_id = fields.Many2one('membership.city.handlers', required=True, readonly=True, default=_default_city)
   state = fields.Selection(selection=[('new', 'New')], default='new')
   is_special_subcity = fields.Boolean(default=False, string="Is City?")
   annual_plan_subcity_state = fields.Integer(compute="annual_plan_subcity_amount")
   bypass_plannig = fields.Boolean(default=False)
   weredas = fields.Boolean(default=False)
   make_readonly = fields.Boolean(default=False)
   total = fields.Integer(store=True, compute="_check_if_it_has_weredas")
   unique_representation_code = fields.Char(translate=True, size=6, required=True)
   
   _sql_constraints = [
      ('name_constraint', 'unique(name)', ' Subcity/Sector must be unique.'),
   ]

   @api.model
   def create(self, vals):
      """This will make sure field is true"""
      res = super(MembershipHandlersParent, self).create(vals)
      res.make_readonly = True
      return res


   def unlink(self):
      """This function will deny deletion if the record has woreda"""
      for record in self:
         if len(record.branch_ids.ids) > 0:
            raise UserError(_("You Can Not Delete A Sub City That Has a Woreda Under It."))
      return super(MembershipHandlersParent, self).unlink()


   @api.onchange('parent_manager')
   def _readonly_subcity(self):
      """This function will make a readonly"""
      for record in self:
         if record.parent_manager and self.env.user.has_group('member_minor_configuration.member_group_city_transfer_handler'):
            record.make_readonly = True

   def revise_annual_planning(self):
      """This function will make city plans state draft"""
      for record in self:
         plans = self.env['annual.plans.subcity'].search([('fiscal_year.state', '=', 'active'), ('subcity_id', '=', record.id), ('state', '=', 'approved')])
         if plans:
            for plan in plans:
               self.env['revised.plan.history'].sudo().create({
                  'name_subcity': plan.id,
                  'of_subcity': True,
                  'type_of_member': plan.type_of_member,
                  'male': plan.male,
                  'female': plan.female,
                  'total_estimated': plan.total_estimated,
                  'fiscal_year': plan.fiscal_year.id,
                  'approved_date': plan.approved_date,
                  'revised_date': date.today(),
                  'subcity_id': record.id,
               })
               plan.state = 'draft'


   def annual_plan_subcity_amount(self):
      """This function will count the approved states"""
      for record in self:
         plans = self.env['annual.plans.subcity'].search([('fiscal_year.state', '=', 'active'), ('subcity_id', '=', record.id)]).filtered(lambda rec: rec.state == 'approved')
         record.annual_plan_subcity_state = len(plans)

   @api.depends('branch_ids')
   def _check_if_it_has_weredas(self):
      """This function will check if the subcity has woredas"""
      for record in self:
         record.total = len(record.branch_ids.ids)
         if record.total > 0:
            record.weredas = True
         else:
            record.weredas = False

   @api.onchange('name')
   def _validate_name(self):
      """This function will validate the name given"""
      for record in self:
         no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
         if record.name:
               for st in record.name:
                  if st.isdigit():
                     raise UserError(_("You Can't Have A Digit in Sub City Name"))

class MembershipHandlersChild(models.Model):
   _name="membership.handlers.branch"
   _description="Woreda Handlers"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_subcity(self):
      """This function will set a default value to wereda"""
      return self.env['membership.handlers.parent'].search([('parent_manager', '=', self.env.user.id)], limit=1).id

   name = fields.Char(required=True, string="Woreda", translate=True, copy=False, track_visibility='onchange', size=64)
   parent_id = fields.Many2one('membership.handlers.parent', string="Subcity", copy=False, required=True, track_visibility='onchange', default=_default_subcity)
   branch_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id","=",self.env.ref("member_minor_configuration.member_group_manager").id)], string="Woreda Leader", required=True, track_visibility='onchange', store=True)
   ict_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("member_minor_configuration.member_group_manager").id)], string="ICT Leader", required=True, track_visibility='onchange', store=True)
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("member_minor_configuration.member_group_complaint_management").id)], required=True, track_visibility='onchange')
   is_special_woreda = fields.Boolean(default=False)
   main_office_ids = fields.One2many('main.office', 'wereda_id', readonly=True, copy=False, track_visibility='onchange', string="Basic Organizations")
   main_office = fields.Boolean(default=False)
   total = fields.Integer(store=True, compute="_check_if_it_has_main_office")
   annual_plan_wereda_state = fields.Integer(compute="annual_plan_wereda_amount")
   bypass_plannig = fields.Boolean(default=False)
   make_readonly = fields.Boolean(default=False)
   unique_representation_code = fields.Char(translate=True, size=6, required=True)


     
   @api.model
   def create(self, vals):
      """This will make sure field is true"""
      res = super(MembershipHandlersChild, self).create(vals)
      res.make_readonly = True
      return res

   def unlink(self):
      """This function will deny deletion if the record has main office"""
      for record in self:
         if len(record.main_office_ids.ids) > 0:
            raise UserError(_("You Can Not Delete A Woreda That Has a Basic Organization Under It."))
      return super(MembershipHandlersChild, self).unlink()


   @api.onchange('branch_manager')
   def _readonly_woreda(self):
      """This function will make a readonly"""
      for record in self:
         if record.branch_manager and self.env.user.has_group('member_minor_configuration.member_group_city_transfer_handler'):
            record.make_readonly = True

   @api.depends('main_office_ids')
   def _check_if_it_has_main_office(self):
      """This function will check if the woreda has main office"""
      for record in self:
         record.total = len(record.main_office_ids.ids)
         if record.total > 0:
            record.main_office = True
         else:
            record.main_office = False


   @api.onchange('parent_id')
   def _remove_all_fields(self):
      """This function will make visible fields nulll when they change subcity"""
      for record in self:
         if record.parent_id and record.main_office == False:
            record.name = False
            record.branch_manager = False
            record.complaint_handler = False

   def revise_annual_planning(self):
      """This function will make city plans state draft"""
      for record in self:
         plans = self.env['annual.plans.wereda'].search([('fiscal_year.state', '=', 'active'), ('wereda_id', '=', record.id), ('state', '=', 'approved')])
         if plans:
            for plan in plans:
               self.env['revised.plan.history'].sudo().create({
                  'name_wereda': plan.id,
                  'of_wereda': True,
                  'type_of_member': plan.type_of_member,
                  'male': plan.male,
                  'female': plan.female,
                  'total_estimated': plan.total_estimated,
                  'fiscal_year': plan.fiscal_year.id,
                  'approved_date': plan.approved_date,
                  'revised_date': date.today(),
                  'wereda_id': record.id,
               })
               plan.state = 'draft'

   def annual_plan_wereda_amount(self):
      for record in self:
         plans = self.env['annual.plans.wereda'].search([('fiscal_year.state', '=', 'active'), ('wereda_id', '=', record.id)]).filtered(lambda rec: rec.state == 'approved')
         record.annual_plan_wereda_state = len(plans)
