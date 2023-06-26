"""This file will deal with the modification to be made on the members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date

class ArchivedInformation(models.Model):
    _name = "archived.information"
    _description = "This will handle archiving_information"


    donor_id = fields.Many2one('donors')
    supporter_id = fields.Many2one('supporter.members')
    candidate_id = fields.Many2one('candidate.members')
    member_id = fields.Many2one('res.partner')
    demote_to_for_leader = fields.Selection(selection=[('member', 'Member'), ('candidate', 'Candidate'), ('supporter', 'Supporter')], default='member')
    demote_to_for_member = fields.Selection(selection=[('candidate', 'Candidate'), ('supporter', 'Supporter')], default='candidate')
    date_from = fields.Date()
    date_to = fields.Date()
    departure_reason = fields.Selection(selection=[('fired', 'Fired'), ('demote', 'Demote'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)
    archived = fields.Boolean(default=False)

class LeagueOrganization(models.Model):
    _name = "membership.organization"
    _description = "This will handle member's Organization"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange')


class LeagueResponsibility(models.Model):
    _name="league.responsibility"
    _description="This will handle leagues's responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange')

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


class UserInput(models.Model):
    _name="user.input"
    _description="This will create user inputs"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    model = fields.Char(required=True)
    user_input = fields.Char(required=True)


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

    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True, store=True)
    age = fields.Integer(readonly=True, store=True)
    date = fields.Date(string="Date of Birth", store=True)
    ethnic_group = fields.Many2one('ethnic.groups', required=True, store=True)
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region")
    region_of_birth = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Birth Place Region", store=True)
    zone_city_of_birth = fields.Char(translate=True, string="Zone/City of Birth", store=True)
    wereda_of_birth = fields.Char(translate=True, string="Woreda of Birth", store=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    league_type = fields.Selection(selection=[('young', 'Youngsters'), ('women', 'Women')], track_visibility='onchange', readonly=True)
    league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange')
    membership_org = fields.Many2one('membership.organization', track_visibility='onchange', readonly=True)
    league_responsibility = fields.Many2one('league.responsibility', track_visibility='onchange')
    league_status = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], default='league member', track_visibility='onchange')
    other_trainings = fields.Char(translate=True)
    income = fields.Float(store=True, track_visibility='onchange')
    work_experience_ids = fields.One2many('work.experience', 'partner_id')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    house_number = fields.Char()
    attachment_amount = fields.Integer(compute="_count_attachments")
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, store=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, store=True, track_visibility='onchange')
    kebele = fields.Char(translate=True)
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    start_of_league = fields.Selection(selection=[(str(num), num) for num in range(2001, (datetime.now().year)+1 )], string='League Start Year')
    grade = fields.Selection(selection=[('very high', 'Very High'), ('high', 'High'), ('mid', 'Mid'), ('low', 'Low'), ('very low', 'Very Low')], default='low', required=True, track_visibility='onchange')
    payment_method = fields.Selection(selection=[('cash', 'Cash'), ('percentage', 'Percentage')], required=True, default="cash")
    membership_monthly_fee_cash = fields.Float(store=True, track_visibility='onchange')
    membership_monthly_fee_cash_from_percent = fields.Float(readonly=True, store=True, track_visibility='onchange')
    membership_monthly_fee_percent = fields.Float(readonly=True, store=True)
    key_strength = fields.Many2many('interpersonal.skills', 'positive_skill_rel', domain="[('positive', '=', True)]", translate=True, track_visibility='onchange')
    key_weakness = fields.Many2many('interpersonal.skills', domain="[('positive', '=', False)]", translate=True, track_visibility='onchange')
    is_leader = fields.Boolean(string="Is Leader", default=False)
    educational_history = fields.One2many('education.history', 'partner_id')
    training_counter = fields.Integer(compute="_count_trainings", string="Trainings Taken")
    main_office = fields.Many2one('main.office', readonly="1", domain="['&', '&', ('for_which_members', '=', 'member'), ('member_main_type_id', '=', membership_org), ('wereda_id', '=', wereda_id)]", store=True, track_visibility='onchange')
    member_cells = fields.Many2one('member.cells', readonly="1", domain="[('main_office', '=', main_office)]", store=True, track_visibility='onchange')
    league_main_office = fields.Many2one('main.office', readonly="1", domain="['&', '&', ('wereda_id', '=', wereda_id), ('for_which_members', '=', 'league'), ('league_main_type_id', '=', league_org)]", store=True, track_visibility='onchange')
    league_member_cells = fields.Many2one('member.cells', readonly="1", domain="[('main_office', '=', league_main_office)]", store=True, track_visibility='onchange')
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
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', track_visibility='onchange')
    leader_stock = fields.Selection(selection=[('appointed', 'Appointed'), ('not appointed', 'Not Appointed')], default='not appointed', track_visibility='onchange', readonly=True)
    type_of_payment = fields.Selection(selection=[('in person', 'In Person'), ('bank', 'Bank')], default='in person', required=True)
    user_name = fields.Char(readonly=True)
    email_address = fields.Char()
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    supporter_id = fields.Many2one('supporter.members', readonly=True)
    evaluation_main_points = fields.Text(string='Evaluation Main Points', translate=True)
    decision = fields.Text(string="Decision", translate=True)
    evaluated = fields.Boolean(default=False)
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    experience = fields.Char(translate=True, string="Experience Year")
    pay_for_league = fields.Boolean(default=False)
    league_payment = fields.Float(store=True, track_visibility='onchange')
    track_member_fee = fields.Float(store=True, readonly="1")
    track_league_fee = fields.Float(store=True, readonly="1")
    archive_ids = fields.One2many('archived.information', 'member_id')
    appropriate_age = fields.Boolean(default=False)
    national_id = fields.Char(translate=True, track_visibility='onchange')
    payed_for_id = fields.Boolean(default=False)
    is_woman = fields.Boolean(default=False)
    has_user_name = fields.Boolean(default=False)
    member_ids = fields.Char(copy=False, readonly=True)
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True)
    complaint_amount = fields.Integer(compute="total_complaint_amount")
    pending_transfer_amount = fields.Integer(compute="total_pending_transfer_amount")
    member_password_verfiy =  fields.Boolean(string="Verfiy User", default="f")
    assembly_counter = fields.Integer(compute="total_assembly")
    demote = fields.Boolean(default=False)

    def action_portal_reset_member_password(self):
        for record in self:
            res = self.env['res.users'].sudo().search([('partner_id','=', record.id)], limit=1)
            password = "123456"
            res.sudo().update({
                'password': password
            })
            record.update({
                'member_password_verfiy': False
            })
            user = self.env.user
            message = "The User Name For " + str(record.name) + " Is " + str(record.user_name) + ", password is 123456. Please Advise The Member To Change This Passport After They Login." 
            user.notify_success(message, '<h4>User Name</h4>', True)

    def unlink(self):
        """This function will deny deleteion of memebr, league or leader"""
        for record in self:
            if record.is_member or record.is_league or record.is_leader:
                raise UserError(_("You Can Only Archive Members, Leagues Or Leaders"))
        return super(Partner, self).unlink()
        

    def make_birthday_change_for_member(self):
        """This function will increase birthdays every year"""
        today = date.today()
        members = self.env['res.partner'].search(['|', '|', '|', ('is_league', '=', True), ('is_leader', '=', True), ('is_member', '=', True)]).filtered(lambda rec: rec.date != False).filtered(lambda rec: rec.date.month == today.month).filtered(lambda rec: rec.date.day == today.day)
        for member in members:
            if member.age < (today.year - member.date.year):
                member.age += 1

    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.members.wizard'].create({
            'member_id': self.id
        })
        return {
            'name': _('Why Do You Want To Archive This Record?'),
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
            record.candidate_id.active = True
            record.supporter_id.active = True
            all_archived = self.env['archived.information'].search([('member_id', '=', record.id)])
            for archive in all_archived:
                if archive.archived:
                    archive.archived = False
                    archive.date_to = date.today()

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

    @api.onchange('date')
    def _chnage_age(self):
        """This function will change the age of person based on date"""
        for record in self:
            if record.date:
                today = date.today()
                if record.date >= today:
                    raise UserError(_("You Have To Pick A Date Before Today."))
                if today.month < record.date.month:
                    record.age = (today.year - record.date.year) - 1
                else:
                    if today.month == record.date.month and today.day < record.date.day:
                        record.age = (today.year - record.date.year) - 1
                    else:
                        record.age = today.year - record.date.year

    @api.onchange('league_type', 'gender')
    def _league_type_modification(self):
        """This function will check if gender and league type work together"""
        for record in self:
            if record.league_type == 'women' and record.gender == 'Male':
                raise ValidationError(_('Only Females Can Join The Women League'))


    def _count_trainings(self):
        """This function will count the number of trainings took by a leader"""
        for record in self:
            training = self.env['leaders.trainings'].search([('partner_id', '=', record.id)])
            if training:
                record.training_counter = len(training.ids)
            else:
                record.training_counter = 0


    @api.onchange('subcity_id')
    def _change_all_field_for_member(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False

    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 101:
                    record.is_user_input = False
                else:
                    record.is_user_input = True


    @api.onchange('member_responsibility')
    def _change_stock(self):
        for record in self:
            if record.member_responsibility.id == 2 or record.member_responsibility.id == 3:
                record.stock = 'selected'
            else:
                record.stock = 'not selected'


    @api.onchange('league_payment')
    def _assign_league_fee(self):
        """This function will modify league payment chnage in cells"""
        for record in self:
            league = record.league_member_cells.leagues_ids.filtered(lambda rec: rec.id == record._origin.id)
            league_2 = record.league_member_cells.league_leaders_ids.filtered(lambda rec: rec.id == record._origin.id)
            if league:
                previous = league.league_payment
                total_main_fee = record.league_main_office.total_leagues_fee - previous
                main_fee = record.league_main_office.total_league_fee - previous
                record.league_main_office.total_leagues_fee = total_main_fee + record.league_payment
                record.league_main_office.total_league_fee = main_fee + record.league_payment
                cell_fee = record.league_member_cells.total_membership_fee - previous
                league_fee = record.league_member_cells.total_league_fee - previous
                record.league_member_cells.total_membership_fee = cell_fee + record.league_payment
                record.league_member_cells.total_league_fee = league_fee + record.league_payment

            if league_2:
                previous = league_2.league_payment
                total_main_fee = record.league_main_office.total_leagues_fee - previous
                main_fee = record.league_main_office.total_league_fee - previous
                record.league_main_office.total_leagues_fee = total_main_fee + record.league_payment
                record.league_main_office.total_league_fee = main_fee + record.league_payment
                cell_fee = record.league_member_cells.total_membership_fee - previous
                league_fee = record.league_member_cells.total_leader_league_fee - previous
                record.league_member_cells.total_membership_fee = cell_fee + record.league_payment
                record.league_member_cells.total_leader_league_fee = league_fee + record.league_payment


    @api.onchange('membership_monthly_fee_cash', 'membership_monthly_fee_cash_from_percent')
    def _assign_membership_fee_to_member(self):
        """This function will modify membership payment of members change in cells"""
        for record in self:
            member = record.member_cells.members_ids.filtered(lambda rec: rec.id == record._origin.id)
            member_2 = record.member_cells.leaders_ids.filtered(lambda rec: rec.id == record._origin.id)
            if member:
                previous = member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent
                current = record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent
                total_main_fee = record.main_office.total_membership_fee - previous
                main_fee = record.main_office.total_member_fee - previous
                record.main_office.total_membership_fee = total_main_fee + current
                record.main_office.total_member_fee = main_fee + current
                total_cell_fee = record.member_cells.total_membership_fee - previous
                cell_fee = record.member_cells.total_member_fee - previous
                record.member_cells.total_membership_fee = total_cell_fee + current
                record.member_cells.total_member_fee = cell_fee + current

            if member_2:
                previous = member_2.membership_monthly_fee_cash + member_2.membership_monthly_fee_cash_from_percent 
                current = record.membership_monthly_fee_cash + record.membership_monthly_fee_cash_from_percent
                total_main_fee = record.main_office.total_membership_fee - previous
                main_fee = record.main_office.total_member_fee - previous
                record.main_office.total_membership_fee = total_main_fee + current
                record.main_office.total_member_fee = main_fee + current
                total_cell_fee = record.member_cells.total_membership_fee - previous
                cell_fee = record.member_cells.total_leader_fee - previous
                record.member_cells.total_membership_fee = total_cell_fee + current
                record.member_cells.total_leader_fee = cell_fee + current

    @api.onchange('pay_for_league')
    def _change_league(self):
        """This functionw will make value null"""
        for record in self:
            if record.pay_for_league:
                record.league_payment = 0.00

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                if len(record.phone) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.phone[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))


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
            all_league_payment = self.env['each.league.payment'].search([('league_id', '=', record._origin.id), ('year', '=', year.id)])
            if all_league_payment:
                record.write({
                    'league_payments': [(6, 0, all_league_payment.ids)]
                })

    @api.onchange('demote_to_member')
    def _demote_to_member(self):
        """This function will demote a leader to a member"""
        for record in self:
            if record.demote_to_member:
                record.is_leader = False


    @api.onchange('payment_method')
    def _change_payment_method(self):
        """This function will change values based on payment methosd"""
        for record in self:
            if record.payment_method == 'cash':
                record.membership_monthly_fee_percent = 0.00
                record.membership_monthly_fee_cash_from_percent = 0.00
            else:
                record.membership_monthly_fee_cash = 0.00

    @api.onchange('income')
    def _compute_according_to_income(self):
        """This will compute methods of payments based on your income"""
        for record in self:
            # if record.income == 0.00:
            #     record.payment_method = 'cash'
            #     record.membership_monthly_fee_cash = 0.00
            # else:
            all_fee = self.env['payment.fee.configuration'].search([])
            if all_fee:
                for fee in all_fee:
                    if fee.minimum_wage <= record.income <= fee.maximum_wage:
                        record.membership_monthly_fee_percent = fee.fee_in_percent
                        record.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * record.income
                        break
                    else:
                        record.membership_monthly_fee_percent = fee.fee_in_percent
                        record.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * record.income
                        continue
            else:
                raise UserError(_("Please Corrected The Membership Fee from Income Configuration."))


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
                raise UserError(_("A Member Who Is 15 Or Below Can't Be A Leader!"))
            if record.is_member == True:
                if record.stock == 'not selected':
                    raise UserError(_("A Member Who Is Not Selected Can Not Be A Leader!"))
                wizard = self.env['create.leader.wizard'].create({
                    'member_id': record.id,
                    'national_id': record.national_id,
                    'membership_org': record.membership_org.id,
                    'member_ids': record.member_ids,
                    'start_of_membership': record.start_of_membership
                })
                return {
                    'name': _('Create Leader Wizard'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'create.leader.wizard',
                    'view_mode': 'form',
                    'res_id': wizard.id,
                    'target': 'new'
                }

            if record.is_league == True:
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

            if record.is_league == False and record.is_member == False:
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

    def create_league(self):
        """This function will create leagues from membership"""
        for record in self:
            if record.age < 15:
                raise ValidationError(_("A Person Who Is 15 Or Below Can't Be A League"))
            if (record.is_member == True or record.is_member == False or record.is_leader == True or record.is_leader == False) and record.is_league == False:
                if record.gender == 'Male' and record.age > 35:
                   raise ValidationError(_("A Member who is a Male and Above 35 can\'t become a League")) 
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


    def print_id(self):
        """This will print ID of a member"""
        for record in self:
            return self.env.ref('members_custom.create_member_id').report_action(record._origin.id)

    def print_certificate(self):
        """This will print Certificate of a member"""
        for record in self:
            return self.env.ref('members_custom.create_certificate').report_action(record._origin.id)        


    def total_complaint_amount(self):
        """This function will calculate number of complaints"""
        for record in self:
            complaints = self.env['member.complaint'].search([('victim_id', '=', record.id)])
            if complaints:
                record.complaint_amount = len(complaints.ids)
            else:
                record.complaint_amount = 0


    def total_pending_transfer_amount(self):
        """This function will calculate the number of tramsfers"""
        for record in self:
            transfers = self.env['members.transfer'].search([('partner_id', '=', record.id), ('state', '!=', ['review', 'waiting for approval'])])
            if transfers:
                record.pending_transfer_amount = len(transfers.ids)
            else:
                record.pending_transfer_amount = 0

    def total_assembly(self):
        """This function will count assembly where member participated"""
        for record in self:
            assembly = self.env['member.assembly'].search([('partner_id', '=', record.id)])
            if assembly:
                record.assembly_counter = len(assembly.ids)
            else:
                record.assembly_counter = 0