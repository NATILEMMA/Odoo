"""This file will deal with the modification to be made on the members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date

class LeagueOrganization(models.Model):
    _name = "membership.organization"
    _description = "This will handle member's Organization"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange')

# class MembershipOrganization(models.Model):
#     _name = "league.organization"
#     _description = "This will handle league's Organization"

#     name = fields.Char(translate=True, required=True)

class MemberResponsibility(models.Model):
    _name="members.responsibility"
    _description="This will handle member's responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange')


class LeaderResponsibility(models.Model):
    _name="leaders.responsibility"
    _description="This will handle leader's responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange')


class TrainingCenters(models.Model):
    _name="training.centers"
    _description="This will handle training centers for leaders"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name= fields.Char(translate=True, required=True, track_visibility='onchange')



class Stages(models.Model):
    _name="membership.stage"
    _description="This model will create different grades for members"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, string="Membership Stage", translate=True)
    color = fields.Integer()

    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each stage must be unique')
                        ]



class EducationLevel(models.Model):
    _name="res.edlevel"
    _description="This model will contain education levels"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, translate=True, track_visibility='onchange')

class FieldofStudy(models.Model):
    _name="field.study"
    _description="This will craete a static fields of study"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, translate=True, track_visibility='onchange')

class WorkExperience(models.Model):
    _name="work.experience"
    _description="This model will create model that will hold history of work experince"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Job Title", translate=True)
    place_of_work = fields.Char(string="Company Name", translate=True)
    years_of_service = fields.Char(translate=True)
    current_job = fields.Boolean(default=False)
    partner_id = fields.Many2one('res.partner', readonly=True)
    candidate_id = fields.Many2one('candidate.members', readonly=True)


class InterpersonalSkills(models.Model):
    _name="interpersonal.skills"
    _description="This model will create models that will contain a list of skills and weaknesses"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, translate=True, track_visibility='onchange')
    positive = fields.Boolean(track_visibility='onchange')

class EthnicGroups(models.Model):
    _name="ethnic.groups"
    _description="This model will create different ethinic groups"

    name = fields.Char(required=True, translate=True, track_visibility='onchange')

class AttachmentTypes(models.Model):
  _name="attachment.type"
  _description="This will handle the different types of attachments the member is allowed to attach"
  _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

  name = fields.Char(required=True, string="Attachment Type", translate=True, track_visibility='onchange')


  _sql_constraints = [
                       ('Check on name', 'UNIQUE(name)', 'Each attachment type must be unique')
                     ]

class LeaderEvaluation(models.Model):
    _name="leader.evaluation"
    _description="This will handle the evaluation of leaders"

    partner_id = fields.Many2one('res.partner')
    evaluation_main_points = fields.Char(translate=True)
    key_strength = fields.Many2many('interpersonal.skills', 'positive_skill_evaluation_rel', domain="[('positive', '=', True)]")
    key_weakness = fields.Many2many('interpersonal.skills', domain="[('positive', '=', False)]")
    grade = fields.Selection(selection=[('very high', 'Very High'), ('high', 'High'), ('mid', 'Mid'), ('low', 'Low'), ('very low', 'Very Low')], default='low')
    decision = fields.Char(translate=True)
    evaluated = fields.Boolean(default=False)

    def finish_evaluation(self):
        """This will make a leader evaluated and give him a badge"""
        for record in self:
            record.evaluated = True

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

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    #_inherit = ['ir.attachment', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    attachment_type = fields.Many2one('attachment.type')

class Education(models.Model):
    _name = "education.history"
    _description = "This will create educational history"

    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    partner_id = fields.Many2one('res.partner')
    candidate_id = fields.Many2one('candidate.members')
    supporter_id = fields.Many2one('supporter.members')


class Partner(models.Model):
    _inherit = 'res.partner'
    #_inherit = ['res.partner', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True)
    age = fields.Integer(required=True)
    ethnic_group = fields.Many2one('ethnic.groups')
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region")
    region_of_birth = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Birth Place Region")
    zone_city_of_birth = fields.Char(translate=True, string="Zone/City of Birth")
    wereda_of_birth = fields.Char(translate=True, string="Woreda of Birth")
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    league_type = fields.Selection(selection=[('young', 'Youngsters'), ('women', 'Women')], track_visibility='onchange')
    league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange', readonly=True)
    membership_org = fields.Many2one('membership.organization', track_visibility='onchange', readonly=True)
    league_status = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], default='league member', track_visibility='onchange')
    other_trainings = fields.Char(translate=True)
    income = fields.Float(store=True, track_visibility='onchange')
    work_experience_ids = fields.One2many('work.experience', 'partner_id')
    member_complaint_ids = fields.One2many('member.complaint', 'victim_id', track_visibility='onchange')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    house_number = fields.Char()
    attachment_amount = fields.Integer(compute="_count_attachments")
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, store=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, store=True, track_visibility='onchange')
    kebele = fields.Char(translate=True)
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    start_of_league = fields.Selection(selection=[(str(num), num) for num in range(2001, (datetime.now().year)+1 )], string='League Start Year')
    grade = fields.Selection(selection=[('very high', 'Very High'), ('high', 'High'), ('mid', 'Mid'), ('low', 'Low'), ('very low', 'Very Low')], default='low', required=True, track_visibility='onchange')
    payment_method = fields.Selection(selection=[('cash', 'Cash'), ('percentage', 'Percentage')], readonly=True, store=True)
    membership_monthly_fee_cash = fields.Float(store=True, track_visibility='onchange')
    membership_monthly_fee_cash_from_percent = fields.Float(readonly=True, store=True, track_visibility='onchange')
    membership_monthly_fee_percent = fields.Float(readonly=True, store=True)
    key_strength = fields.Many2many('interpersonal.skills', 'positive_skill_rel', domain="[('positive', '=', True)]", translate=True, track_visibility='onchange')
    key_weakness = fields.Many2many('interpersonal.skills', domain="[('positive', '=', False)]", translate=True, track_visibility='onchange')
    is_leader = fields.Boolean(string="Is Leader", default=False)
    educational_history = fields.One2many('education.history', 'partner_id')
    training_ids = fields.One2many('leaders.trainings', 'partner_id', track_visibility='onchange')
    training_counter = fields.Integer(compute="_count_trainings", string="Trainings Taken")
    main_office = fields.Many2one('main.office', domain="['&', '&', ('for_which_members', '=', 'member'), ('member_main_type_id', '=', membership_org), ('wereda_id', '=', wereda_id)]", store=True, track_visibility='onchange')
    member_cells = fields.Many2one('member.cells', domain="[('main_office', '=', main_office)]", store=True, track_visibility='onchange')
    league_main_office = fields.Many2one('main.office', domain="['&', '&', ('wereda_id', '=', wereda_id), ('for_which_members', '=', 'league'), ('league_main_type_id', '=', league_org)]", store=True, track_visibility='onchange')
    league_member_cells = fields.Many2one('member.cells', domain="[('main_office', '=', league_main_office)]", store=True, track_visibility='onchange')
    member_responsibility = fields.Many2one('members.responsibility', track_visibility='onchange')
    leader_responsibility = fields.Many2one('leaders.responsibility', track_visibility='onchange')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True)
    demote_to_member = fields.Boolean(default=False, track_visibility='onchange')
    year_of_payment = fields.Many2one("fiscal.year", string='Year', store=True)
    membership_payments = fields.One2many('each.member.payment', 'member_id', domain="[('year', '=', year_of_payment)]", track_visibility='onchange')
    league_payments = fields.One2many('each.league.payment', 'league_id', domain="[('year', '=', year_of_payment)]", track_visibility='onchange')
    is_leader = fields.Boolean(string="Is Leader", default=False)
    is_league = fields.Boolean(default=False)
    is_member = fields.Boolean(default=False)
    was_supporter = fields.Boolean(default=False)
    was_candidate = fields.Boolean(default=False)
    was_member = fields.Boolean(default=False)
    was_league = fields.Boolean(default=False)
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', track_visibility='onchange', readonly=True)
    leader_stock = fields.Selection(selection=[('appointed', 'Appointed'), ('not appointed', 'Not Appointed')], default='not appointed', track_visibility='onchange', readonly=True)
    type_of_payment = fields.Selection(selection=[('in person', 'In Person'), ('bank', 'Bank')], default='in person', required=True)
    user_name = fields.Char(readonly=True)
    email_address = fields.Char()
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    supporter_id = fields.Many2one('supporter.members', readonly=True)
    evaluation_ids = fields.One2many('leader.evaluation', 'partner_id', track_visibility='onchange')
    evaluation_main_points = fields.Text(string='Evaluation Main Points', translate=True)
    decision = fields.Text(string="Decision", translate=True)
    evaluated = fields.Boolean(default=False)
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    member_transfer = fields.One2many('members.transfer', 'partner_id', track_visibility='onchange')
    experience = fields.Char(translate=True)
    pay_for_league = fields.Boolean(default=False)
    league_payment = fields.Float(store=True, track_visibility='onchange')
    track_member_fee = fields.Float(store=True, readonly=True)
    track_league_fee = fields.Float(store=True, readonly=True)
    reason = fields.Text(translate=True, track_visibility='onchange')
    appropriate_age = fields.Boolean(default=False)
    national_id = fields.Char(translate=True, track_visibility='onchange')
    payed_for_id = fields.Boolean(default=False)
    is_woman = fields.Boolean(default=False)
    has_user_name = fields.Boolean(default=False)
    member_ids = fields.Char(copy=False, readonly=True)


    # @api.model
    # def create(self, vals):
    #     """This function will check if a record already exists"""
    #     exists = self.env['res.partner'].search([('name', '=', vals['name'])])
    #     if exists:
    #         raise UserError(_("A partner with the same name already exists, Please make sure it isn't a duplicated data"))
    #     return super(Partner, self).create(vals)

    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.members.wizard'].create({
            'reason': self.reason
        })
        return {
            'name': _('Archive Members Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.members.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            user = self.env['res.users'].search([('partner_id', '=', record.id), ('active', '=', False)])
            if user:
                user.write({
                    'active': True
                })
            record.active = True

    def add_attachment(self):
        """This function will add attachments"""
        for record in self:
            wizard = self.env['attachment.wizard'].create({
                'res_id': record.id,
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

    @api.onchange('age')
    def _leage_age_adjustments(self):
        """This function will check if age and status of membership"""
        for record in self:
            if record.age >= 18 and record.is_league == True and record.is_member == False and record.is_leader == False:
                record.appropriate_age = True
            else:
                record.appropriate_age = False             

    @api.onchange('league_type', 'gender')
    def _league_type_modification(self):
        """This function will check if gender and league type work together"""
        for record in self:
            if record.league_type == 'women' and record.gender == 'Male':
                raise ValidationError(_('Only Females Can Join The Women League'))

    @api.depends('training_ids')
    def _count_trainings(self):
        """This function will count the number of trainings took by a leader"""
        for record in self:
            record.training_counter = len(record.training_ids)

    @api.onchange('pay_for_league')
    def _dont_pay_league(self):
        """This function will make league payment 0"""
        for record in self:
            if record.pay_for_league == False:
                record.league_payment = 0.00


    @api.onchange('member_responsibility')
    def _change_stock(self):
        for record in self:
            if record.member_responsibility.id == 2 or record.member_responsibility.id == 3:
                record.stock = 'selected'
            else:
                record.stock = 'not selected'

    # @api.onchange('league_payment')
    # def _assign_league_fee(self):
    #     """This function will modify league payment chnage in cells"""
    #     for record in self:
    #         if record.league_member_cells and record.is_league and record.league_status == 'league member':
    #             league = self.env['member.cells'].search([('id', '=', record.league_member_cells.id)]).leagues_ids.filtered(lambda rec: rec.id == record._origin.id)
    #             previous = league.league_payment
    #             main_fee = record.league_main_office.total_leagues_fee - previous
    #             record.league_main_office.total_leagues_fee = main_fee + record.league_payment
    #             cell_fee = record.league_member_cells.total_membership_fee - previous
    #             record.league_member_cells.total_membership_fee = cell_fee + record.league_payment
    #             total_fee = record.league_member_cells.total_membership_fee - previous
    #             record.league_member_cells.total_membership_fee= total_fee + record.league_payment

    #         if record.league_member_cells and record.is_league and record.league_status == 'league leader':
    #             league = self.env['member.cells'].search([('id', '=', record.league_member_cells.id)]).league_leaders_ids.filtered(lambda rec: rec.id == record._origin.id)
    #             previous = league.league_payment
    #             main_fee = record.league_main_office.total_leagues_fee - previous
    #             record.league_main_office.total_leagues_fee = main_fee + record.league_payment
    #             cell_fee = record.league_member_cells.total_membership_fee - previous
    #             record.league_member_cells.total_membership_fee = cell_fee + record.league_payment
    #             total_fee = record.league_member_cells.total_membership_fee - previous
    #             record.league_member_cells.total_membership_fee = total_fee + record.league_payment


    # @api.onchange('membership_monthly_fee_cash', 'membership_monthly_fee_cash_from_percent')
    # def _assign_membership_fee_to_member(self):
    #     """This function will modify membership payment of members change in cells"""
    #     for record in self:
    #         if record.member_cells and record.is_member:
    #             member = self.env['member.cells'].search([('id', '=', record.member_cells.id)]).members_ids.filtered(lambda rec: rec.id == record._origin.id)
    #             previous = member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent
    #             main_fee = record.main_office.total_membership_fee - previous
    #             record.main_office.total_membership_fee = main_fee + record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent
    #             cell_fee = record.member_cells.total_membership_fee - previous
    #             record.member_cells.total_membership_fee = cell_fee + record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent
    #             total_fee = record.member_cells.total_membership_fee - previous
    #             record.member_cells.total_membership_fee = total_fee + record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent

    #         if record.member_cells and record.is_leader:
    #             leader = self.env['member.cells'].search([('id', '=', record.member_cells.id)]).leaders_ids.filtered(lambda rec: rec.id == record._origin.id)
    #             previous = leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent
    #             main_fee = record.main_office.total_membership_fee - previous
    #             record.main_office.total_membership_fee = main_fee + record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent
    #             cell_fee = record.member_cells.total_membership_fee - previous
    #             record.member_cells.total_membership_fee = cell_fee + record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent
    #             total_fee = record.member_cells.total_membership_fee - previous
    #             record.member_cells.total_membership_fee = total_fee + record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent


    @api.onchange('year_of_payment')
    def _generate_payments(self):
        """This function will generate the payment of previous years"""
        for record in self:
            record.membership_payments = [(5, 0, 0)]
            year = self.env['fiscal.year'].search([('id', '=', record.year_of_payment.id)])
            all_payment = self.env['each.member.payment'].search([('member_id', '=', record._origin.id), ('year', '=', year.id)])
            if all_payment:
                record.write({
                    'membership_payments': [(6, 0, all_payment.ids)]
                })

    @api.onchange('demote_to_member')
    def _demote_to_member(self):
        """This function will demote a leader to a member"""
        for record in self:
            if record.demote_to_member:
                record.is_leader = False


    @api.onchange('income')
    def _compute_according_to_income(self):
        """This will compute methods of payments based on your income"""
        for record in self:
            if record.income == 0.00:
                record.payment_method = 'cash'
                record.membership_monthly_fee_cash = 0.00
            else:
                all_fee = self.env['payment.fee.configuration'].search([])
                for fee in all_fee:
                    if fee.minimum_wage <= record.income <= fee.maximum_wage:
                        record.payment_method = 'percentage'
                        record.membership_monthly_fee_percent = fee.fee_in_percent
                        record.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * record.income
                        break
                    else:
                        record.payment_method = 'percentage'
                        record.membership_monthly_fee_percent = fee.fee_in_percent
                        record.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * record.income
                        continue

    def _count_attachments(self):
        """This function will count the number of attachments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0


    def create_leader(self):
        """This function will create a leader from membership"""
        for record in self:
            if record.age < 15:
                raise UserError(_("A Member Who Is Not 15 Or Above Can't Be A Leader"))
            if record.is_member == True:
                wizard = self.env['create.leader.wizard'].create({
                    'member_id': record.id
                })
                return {
                    'name': _('Create Leader Wizard'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'create.leader.wizard',
                    'view_mode': 'form',
                    'res_id': wizard.id,
                    'target': 'new'
                }
            else:
                raise ValidationError(_("This option is for those who are Full Members"))

    def create_league(self):
        """This function will create leagues from membership"""
        for record in self:
            if record.age < 15:
                raise ValidationError(_("A Person Who Is Not 15 Or Above Can't Be A League"))
            if record.is_member == True and record.is_league == False:
                if record.gender == 'Male' and record.age > 35:
                   raise ValidationError(_("A Member who is a Male and Above 24 can\'t become a League")) 

            wizard = self.env['create.league.wizard'].create({
                'league_id': record.id
            })
            return {
                'name': _('Create League Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.league.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }

    def create_member(self):
        """This function will create a member when a league is 18"""
        for record in self:
            wizard = self.env['create.from.league.wizard'].create({
                'member_id': record.id
            })
            return {
                'name': _('Create Members Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.from.league.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }
        