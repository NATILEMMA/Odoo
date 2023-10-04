"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class RevisedPlanHistory(models.Model):
   _name = "revised.plan.history"
   _description = "This model will contain the history of the planned annual"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']



   name_wereda = fields.Many2one('annual.plans.wereda', readonly=True)
   name_subcity = fields.Many2one('annual.plans.subcity', readonly=True)
   name_city = fields.Many2one('annual.plans', readonly=True)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], readonly=True)
   male = fields.Integer(readonly=True)
   female = fields.Integer(readonly=True)
   approved_date = fields.Date(readonly=True)
   revised_date = fields.Date(readonly=True)
   fiscal_year = fields.Many2one("fiscal.year", readonly=True)
   wereda_id = fields.Many2one('membership.handlers.branch', readonly=True)
   of_wereda = fields.Boolean(default=False)
   subcity_id = fields.Many2one('membership.handlers.parent', readonly=True)
   of_subcity = fields.Boolean(default=False)
   city_id = fields.Many2one('membership.city.handlers', readonly=True)
   of_city = fields.Boolean(default=False)
   total_estimated = fields.Integer(readonly=True)


class AnnualPlanReport(models.Model):
   _name = "annual.plan.report"
   _description = "This model will handle the reporting of Annual Plannings"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(required=True, translate=True)
   annual_plan_wereda_id = fields.Many2one('annual.plans.wereda')
   annual_plan_subcity_id = fields.Many2one('annual.plans.subcity')
   annual_plan_city_id = fields.Many2one('annual.plans')
   type_of_member_wereda = fields.Selection(related='annual_plan_wereda_id.type_of_member', store=True)
   type_of_member_subcity = fields.Selection(related='annual_plan_subcity_id.type_of_member', store=True)
   type_of_member_city = fields.Selection(related='annual_plan_city_id.type_of_member', store=True)
   year = fields.Many2one("fiscal.year", string='Year', required=True)
   date_from = fields.Date(required=True)
   date_to = fields.Date(required=True)
   registered = fields.Integer()
   accomplished = fields.Float(digits=(12, 2))



class PlanningBasedonField(models.Model):
   _name = "planning.based.on.field"
   _description = "Thos model will handle planning based on suggested field"

   field_for_candidate_supporter = fields.Selection(selection=[('education', 'Education Level'), ('study field', 'Field of Study')], string="Fields for Candidate or Supporters")
   field_for_member = fields.Selection(selection=[('education', 'Education Level'),
                                                   ('study field', 'Field of Study'),
                                                   ('membership organization', 'Membership Organization')], string="Fields for Members or Leaders")
   field_for_league = fields.Selection(selection=[('education', 'Education Level'),
                                                   ('study field', 'Field of Study'),
                                                   ('league type', 'League Type'),
                                                   ('league org', 'League Organization')], string="Fields for Leagues")
   education_level = fields.Many2one('res.edlevel')
   field_of_study_id = fields.Many2one('field.study')
   membership_org = fields.Many2one('membership.organization')
   league_organization = fields.Many2one('membership.organization')
   league_type = fields.Selection(selection=[('young', 'Youngster'), ('women', 'Woman')])
   # league_org = fields.Many2one('membership.organization')
   # league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban')])
   annual_plan_city_id = fields.Many2one('annual.plans')
   annual_plan_subcity_id = fields.Many2one('annual.plans.subcity')
   annual_plan_wereda_id = fields.Many2one('annual.plans.wereda')
   total_estimated = fields.Integer(required=True)
   total_registered = fields.Integer(readonly=True, store=True)
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)


   @api.model
   def create(self, vals):
      """This function will make sure there is always a plan"""
      res = super(PlanningBasedonField, self).create(vals)
      if res.total_estimated == 0:
         raise UserError(_("Please Add The Estimated Amount"))
      return res

class AnnualPlansWereda(models.Model):
   _name="annual.plans.wereda"
   _description="This model will handle the annual members estimation planning in wereda"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_wereda(self):
      active_id = self.env.context.get('active_id')
      return self.env['membership.handlers.branch'].search([('id', '=', active_id)])


   def _default_year(self):
      year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
      if len(year) > 1:
         pass
      else:
         return year.id


   name = fields.Char(readonly=True, size=128)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], required=True, track_visibility='onchange')
   male = fields.Integer(track_visibility='onchange')
   female = fields.Integer(track_visibility='onchange')
   approved_date = fields.Date(store=True)
   fiscal_year = fields.Many2one("fiscal.year", string='Year', required=True, track_visibility='onchange', store=True)
   wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda, readonly=True)
   from_subcity_plan = fields.Many2one('annual.plans.subcity', store=True, required=True, readonly=True)
   total_estimated = fields.Integer(compute="_calculate_total_members_in_wereda", store=True)
   registered_male = fields.Integer(store=True)
   registered_female = fields.Integer(store=True)
   total_registered = fields.Integer(store=True)
   colors = fields.Selection(selection=[('red', 'Red'), ('orange', 'Orange'), ('blue', 'Blue'), ('green', 'Green')], default='orange')
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)
   x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
   state = fields.Selection(selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft', track_visibility='onchange')
   field_based_planning = fields.One2many('planning.based.on.field', 'annual_plan_wereda_id')

   @api.model
   def create(self, vals):
      """This function will make sure duplicate creation for same type in the same year doesn't exist"""
      active_id = self.env.context.get('active_id')
      exists = self.env['annual.plans.wereda'].search([('fiscal_year', '=', vals['fiscal_year']), ('type_of_member', '=', vals['type_of_member']), ('wereda_id', '=', active_id)])
      year = self.env['fiscal.year'].search([('id', '=', vals['fiscal_year'])])
      wereda = self.env['membership.handlers.branch'].search([('id', '=', active_id)])
      if exists:
         raise ValidationError(_("A Plan for %s for %s and Type already exists.") % (wereda.name, year.name))
      if vals['male'] == 0 or vals['female'] == 0:
         raise ValidationError(_("Please Enter An Estimated Number For Either Male or Female"))
      res = super(AnnualPlansWereda, self).create(vals)
      res.name = res.fiscal_year.name + "/" + res.wereda_id.name + "/" + res.type_of_member + " Plan "
      quarter_1 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 1',
                     'annual_plan_wereda_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': res.fiscal_year.date_from,
                     'date_to': res.fiscal_year.date_from + relativedelta(months=3)
                  })

      quarter_2 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 2',
                     'annual_plan_wereda_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_1.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_from + relativedelta(months=6)
                  })

      quarter_3 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 3',
                     'annual_plan_wereda_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_2.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_from + relativedelta(months=9)
                  })

      quarter_4 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 4',
                     'annual_plan_wereda_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_3.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_to
                  })
      return res


   def unlink(self):
      """This function will delete the associated quarters for an annual plan"""
      for record in self:
         if record.state == 'draft':
            quarters = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', record.id)])
            if quarters:
               for quarter in quarters:
                  quarter.unlink()
         else:
            raise UserError(_("You Can Only Delete Plans That Are In Draft State"))
      return super(AnnualPlansWereda, self).unlink() 


   def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
         if (record.state == 'approved'):
               record.x_css = '<style> .o_form_button_edit {display:None}</style>'
         else:
               record.x_css = False


   @api.depends('male', 'female')
   def _calculate_total_members_in_wereda(self):
      """This function will calculate the total members to register"""
      for record in self:
         if record.male or record.female:
            record.total_estimated = record.male + record.female


   @api.onchange('fiscal_year')
   def _default_plan_subcity(self):
      """This function will give the default plan for subcities"""
      for record in self:
         if record.fiscal_year and record.wereda_id:
            record.from_subcity_plan = self.env['annual.plans.subcity'].search([('fiscal_year', '=', record.fiscal_year.id), ('subcity_id', '=', record.wereda_id.parent_id.id), ('state', '=', 'approved'), ('type_of_member', '=', record.type_of_member)])
            if not record.from_subcity_plan:
               raise UserError(_("Please Add Annual Plan For Your Subcity So That Woreda Plan Can Be Based On It."))

   def change_state(self):
      """This function will chnage the state of the annual plan"""
      for record in self:
         if record.total_estimated > 0:
            record.accomplished = (record.total_registered / record.total_estimated) * 100
            if record.accomplished <= 50.00:
               record.colors = 'orange'
            if 50 < record.accomplished < 75:
               record.colors = 'blue'
            if record.accomplished >= 75:
               record.colors = 'green'
         record.approved_date = date.today()
         record.state = 'approved'

class AnnualPlansSubcity(models.Model):
   _name="annual.plans.subcity"
   _description="This model will handle the annual members estimation planning in subcity"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


   def _default_subcity(self):
      active_id = self.env.context.get('active_id')
      return self.env['membership.handlers.parent'].search([('id', '=', active_id)])


   def _default_year(self):
      year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
      if len(year) > 1:
         pass
      else:
         return year.id


   name = fields.Char(readonly=True, size=128)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], required=True, track_visibility='onchange')
   male = fields.Integer(track_visibility='onchange')
   female = fields.Integer(track_visibility='onchange')
   approved_date = fields.Date(store=True)
   fiscal_year = fields.Many2one("fiscal.year", string='Year', required=True, track_visibility='onchange', store=True)
   subcity_id = fields.Many2one('membership.handlers.parent', default=_default_subcity, readonly=True)
   from_city_plan = fields.Many2one('annual.plans', store=True, required=True, readonly=True)
   total_estimated = fields.Integer(compute="_calculate_total_members_in_subcity", store=True)
   registered_male = fields.Integer(store=True)
   registered_female = fields.Integer(store=True)
   total_registered = fields.Integer(store=True)
   colors = fields.Selection(selection=[('red', 'Red'), ('orange', 'Orange'), ('blue', 'Blue'), ('green', 'Green')], default='orange')
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)
   x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
   state = fields.Selection(selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft', track_visibility='onchange')
   field_based_planning = fields.One2many('planning.based.on.field', 'annual_plan_subcity_id')

   @api.model
   def create(self, vals):
      """This function will make sure duplicate creation for same type in the same year doesn't exist"""
      active_id = self.env.context.get('active_id')
      exists = self.env['annual.plans.subcity'].search([('fiscal_year', '=', vals['fiscal_year']), ('type_of_member', '=', vals['type_of_member']), ('subcity_id', '=', active_id)])
      year = self.env['fiscal.year'].search([('id', '=', vals['fiscal_year'])])
      subcity = self.env['membership.handlers.parent'].search([('id', '=', active_id)])
      if exists:
         raise ValidationError(_("A Plan for %s for %s and Type already exists.") % (subcity.name, year.name))
      if vals['male'] == 0 or vals['female'] == 0:
         raise ValidationError(_("Please Enter An Estimated Number For Either Male or Female"))
      res = super(AnnualPlansSubcity, self).create(vals)
      res.name = res.fiscal_year.name + "/" + res.subcity_id.name + "/" + res.type_of_member + " Plan "
      quarter_1 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 1',
                     'annual_plan_subcity_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': res.fiscal_year.date_from,
                     'date_to': res.fiscal_year.date_from + relativedelta(months=3)
                  })

      quarter_2 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 2',
                     'annual_plan_subcity_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_1.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_from + relativedelta(months=6)
                  })

      quarter_3 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 3',
                     'annual_plan_subcity_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_2.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_from + relativedelta(months=9)
                  })

      quarter_4 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 4',
                     'annual_plan_subcity_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_3.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_to
                  })

      return res


   def unlink(self):
      """This function will delete the associated quarters for an annual plan"""
      for record in self:
         if record.state == 'draft':
            quarters = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', record.id)])
            if quarters:
               for quarter in quarters:
                  quarter.unlink()
            wereda_plans = self.env['annual.plans.wereda'].search([('from_subcity_plan', '=', record.id)])
            if wereda_plans:
               raise UserError(_("There are Woreda Plans based on this Sub City Plan. PLease Delete the Woreda Plans first before you proceed."))
         else:
            raise UserError(_("You Can Only Delete Plans That Are In Draft State"))
      return super(AnnualPlansSubcity, self).unlink() 


   def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
         if (record.state == 'approved'):
               record.x_css = '<style> .o_form_button_edit {display:None}</style>'
         else:
               record.x_css = False

   @api.depends('male', 'female')
   def _calculate_total_members_in_subcity(self):
      """This function will calculate the total members to register"""
      for record in self:
         if record.male or record.female:
            record.total_estimated = record.male + record.female

   @api.onchange('fiscal_year')
   def _default_plan_subcity(self):
      """This function will give the default plan for subcities"""
      for record in self:
         if record.fiscal_year and record.subcity_id:
            record.from_city_plan = self.env['annual.plans'].search([('fiscal_year', '=', record.fiscal_year.id), ('city_id', '=', record.subcity_id.city_id.id), ('state', '=', 'approved'), ('type_of_member', '=', record.type_of_member)])
            if not record.from_city_plan:
               raise UserError(_("Please Add Annual Plan For Your City So That Subcity Plan Can Be Based On It."))

   def change_state(self):
      """This function will chnage the state of the annual plan"""
      for record in self:
         if record.total_estimated > 0:
            record.accomplished = (record.total_registered / record.total_estimated) * 100
            if record.accomplished <= 50.00:
               record.colors = 'orange' 
            if 50 < record.accomplished < 75:
               record.colors = 'blue'
            if record.accomplished >= 75:
               record.colors = 'green'
         record.approved_date = date.today()
         record.state = 'approved'

class AnnualPlans(models.Model):
   _name="annual.plans"
   _description="This model will handle the annual members estimation planning"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_city(self):
      active_id = self.env.context.get('active_id')
      return self.env['membership.city.handlers'].search([('id', '=', active_id)])


   def _default_year(self):
      year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
      if len(year) > 1:
         pass
      else:
         return year.id


   name = fields.Char(readonly=True, size=128)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], required=True, track_visibility='onchange')
   male = fields.Integer(track_visibility='onchange')
   female = fields.Integer(track_visibility='onchange')
   approved_date = fields.Date(store=True)
   fiscal_year = fields.Many2one("fiscal.year", string='Year', required=True, track_visibility='onchange', store=True)
   city_id = fields.Many2one('membership.city.handlers', default=_default_city, readonly=True)
   total_estimated = fields.Integer(compute="_calculate_total_members", store=True)
   registered_male = fields.Integer(store=True)
   registered_female = fields.Integer(store=True)
   total_registered = fields.Integer(store=True)
   colors = fields.Selection(selection=[('red', 'Red'), ('orange', 'Orange'), ('blue', 'Blue'), ('green', 'Green')], default='orange')
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)
   x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
   state = fields.Selection(selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft', track_visibility='onchange')
   field_based_planning = fields.One2many('planning.based.on.field', 'annual_plan_city_id')


   @api.model
   def create(self, vals):
      """This function will make sure duplicate creation for same type in the same year doesn't exist"""
      active_id = self.env.context.get('active_id')
      exists = self.env['annual.plans'].search([('fiscal_year', '=', vals['fiscal_year']), ('type_of_member', '=', vals['type_of_member']), ('city_id', '=', active_id)])
      year = self.env['fiscal.year'].search([('id', '=', vals['fiscal_year'])])
      city = self.env['membership.city.handlers'].search([('id', '=', active_id)])
      if exists:
         raise ValidationError(_("A Plan for %s for %s and Type already exists.") % (city.name, year.name))
      if vals['male'] == 0 or vals['female'] == 0:
         raise ValidationError(_("Please Enter An Estimated Number For Either Male or Female"))
      res = super(AnnualPlans, self).create(vals)
      res.name = res.fiscal_year.name + "/" + res.city_id.name + "/" + res.type_of_member + " Plan "
      quarter_1 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 1',
                     'annual_plan_city_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': res.fiscal_year.date_from,
                     'date_to': res.fiscal_year.date_from + relativedelta(months=3)
                  })

      quarter_2 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 2',
                     'annual_plan_city_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_1.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_from + relativedelta(months=6)
                  })

      quarter_3 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 3',
                     'annual_plan_city_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_2.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_from + relativedelta(months=9)
                  })

      quarter_4 = self.env['annual.plan.report'].sudo().create({
                     'name': 'Quarter 4',
                     'annual_plan_city_id': res.id,
                     'year': res.fiscal_year.id,
                     'date_from': quarter_3.date_to + relativedelta(days=1),
                     'date_to': res.fiscal_year.date_to
                  })

      return res

   def unlink(self):
      """This function will delete the associated quarters for an annual plan"""
      for record in self:
         if record.state == 'draft':
            quarters = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', record.id)])
            if quarters:
               for quarter in quarters:
                  quarter.unlink()
            subcity_plans = self.env['annual.plans.subcity'].search([('from_city_plan', '=', record.id)])
            if subcity_plans:
               raise UserError(_("There are Sub City Plans based on this City Plan. PLease Delete the Sub City Plans first before you proceed."))
         else:
            raise UserError(_("You Can Only Delete Plans That Are In Draft State"))
      return super(AnnualPlans, self).unlink() 


   def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
         if (record.state == 'approved'):
               record.x_css = '<style> .o_form_button_edit {display:None}</style>'
         else:
               record.x_css = False


   @api.depends('male', 'female')
   def _calculate_total_members(self):
      """This function will calculate the total members to register"""
      for record in self:
         if record.male or record.female:
            record.total_estimated = record.male + record.female

   def change_state(self):
      """This function will chnage the state of the annual plan"""
      for record in self:
         if record.total_estimated > 0:
            record.accomplished = (record.total_registered / record.total_estimated) * 100
            if record.accomplished <= 50.00:
               record.colors = 'orange'
            if 50 < record.accomplished < 75:
               record.colors = 'blue'
            if record.accomplished >= 75:
               record.colors = 'green'
         record.approved_date = date.today()
         record.state = 'approved'


class ResponsibleBodies(models.Model):
   _name="responsible.bodies"
   _description="This model will handle with the creation of Responsible bodies"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(translate=True, required=True, size=64)
   system_admin = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_user_admin").id)], string="System Adminstrator", required=True, track_visibility='onchange')
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
   city_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_city_admin").id)], string="City Leader", required=True, track_visibility='onchange', store=True) 
   ict_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_city_admin").id)], string="ICT Leader", required=True, track_visibility='onchange', store=True)  
   transfer_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_city_transfer_handler").id)], string="Leaders Transfer Handlers", required=True, track_visibility='onchange')
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_complaint_management").id)], required=True, track_visibility='onchange')
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
         if record.city_manager and self.env.user.has_group('members_custom.member_group_city_transfer_handler'):
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
   parent_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_admin").id)], string="Subcity Leader", copy=False, required=True, track_visibility='onchange', store=True)
   ict_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_admin").id)], string="ICT Leader", copy=False, required=True, track_visibility='onchange', store=True)
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_complaint_management").id)], required=True, track_visibility='onchange')   
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
         if record.parent_manager and self.env.user.has_group('members_custom.member_group_city_transfer_handler'):
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
   branch_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_manager").id)], string="Woreda Leader", required=True, track_visibility='onchange', store=True)
   ict_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_manager").id)], string="ICT Leader", required=True, track_visibility='onchange', store=True)
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_complaint_management").id)], required=True, track_visibility='onchange')
   is_special_woreda = fields.Boolean(default=False)
   main_office_ids = fields.One2many('main.office', 'wereda_id', readonly=True, copy=False, track_visibility='onchange', string="Basic Organizations")
   main_office = fields.Boolean(default=False)
   total = fields.Integer(store=True, compute="_check_if_it_has_main_office")
   annual_plan_wereda_state = fields.Integer(compute="annual_plan_wereda_amount")
   bypass_plannig = fields.Boolean(default=False)
   make_readonly = fields.Boolean(default=False)
   unique_representation_code = fields.Char(translate=True, size=6, required=True)

   # _sql_constraints = [
   #    ('name_constraint', 'unique(name)', 'Woreda must be unique.'),
   # ]

     
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
         if record.branch_manager and self.env.user.has_group('members_custom.member_group_city_transfer_handler'):
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


class Fake(models.Model):
   _name="leader.transfer"
   _description="This model will handle Leader Transfer"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name= fields.Char()