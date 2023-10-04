"""This file will deal with the handling of supporter members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import http


class ImportationModule(models.Model):
    _name="importation.module"
    _description="This model will create Importation Modules"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years


    def _default_years_league(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 2000, -1):
            years.append((str(num), num))
        return years


    def _default_years_member(self):
        """This function will add the years when Meembercould hav been affected"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years


    name = fields.Char(size=128, translate=True)
    first_name  = fields.Char(translate=True, size=32, required=True)
    father_name = fields.Char(translate=True, size=32, required=True)
    grand_father_name = fields.Char(translate=True, size=32, required=True)
    date = fields.Date(string="Date of Birth")
    age = fields.Integer(store=True, compute="_chnage_age")
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], required=True)
    ethnic_group = fields.Many2one('ethnic.groups', required=True)
    region_of_birth = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Birth Place Region/City Administrations", required=True)
    zone_city_of_birth = fields.Char(translate=True, string="Zone/City of Birth", size=64, required=True)
    wereda_of_birth = fields.Char(translate=True, string="Woreda of Birth", size=64, required=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    source_of_livelihood = fields.Selection(selection=[('governmental', 'Governmental'), ('private', 'Private'), ('individual', 'Individual'), ('stay at home', 'Stay At Home')])
    work_place = fields.Char(translate=True, size=64)
    position = fields.Char(translate=True, size=64)
    income = fields.Float()
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, size=64)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True)
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region/City Administrations", required=True)
    residential_subcity = fields.Char(string="Residential Subcity", required=True, store=True)
    residential_wereda = fields.Char(string="Residential Woreda", required=True)
    kebele = fields.Char(translate=True, size=64)
    house_number = fields.Char(translate=True)
    phone = fields.Char(required=True)
    house_phone_number = fields.Char()
    office_phone_number = fields.Char()
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', required=True)
    start_of_support = fields.Selection(selection=_default_years, string='Supporter Start Year')
    email_address = fields.Char()
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True, size=64)
    work_experience_ids = fields.One2many('work.experience', 'import_id')
    educational_history = fields.One2many('education.history', 'import_id')
    is_league = fields.Boolean(default=False, string="Is_League", required=True)
    league_type = fields.Selection(selection=[('young', 'Youngster'), ('women', 'Woman')])
    league_organization = fields.Many2one('membership.organization')
    league_responsibility = fields.Many2one('league.responsibility')
    league_sub_responsibility = fields.Many2one('member.sub.responsibility', string="League's Sub Responsibility")
    start_of_league = fields.Selection(selection=_default_years_league, string='League Start Year')
    league_main_office = fields.Many2one('main.office', string="League Basic Organization", domain="[('member_main_type_id', '=', league_organization), ('wereda_id', '=', wereda_id), ('for_which_members', '=', 'league')]")
    league_member_cells = fields.Many2one('member.cells', domain="[('state', '=', 'active'), ('main_office', '=', league_main_office)]")
    pay_for_league = fields.Boolean(default=False)
    league_payment = fields.Float()
    track_league_fee = fields.Float()
    is_member = fields.Boolean(default=False, string="Is_Member", required=True)
    membership_org = fields.Many2one('membership.organization')
    main_office = fields.Many2one('main.office', string="Basic Organization", domain="[('member_main_type_id', '=', membership_org), ('wereda_id', '=', wereda_id), ('for_which_members', '=', 'member')]")
    member_cells = fields.Many2one('member.cells', domain="[('state', '=', 'active'), ('main_office', '=', main_office)]")
    start_of_membership = fields.Selection(selection=_default_years_member, string='Membership Start Year')
    member_responsibility = fields.Many2one('members.responsibility')
    member_sub_responsibility = fields.Many2one('member.sub.responsibility', string="Member's Sub Responsibility")
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected')
    track_member_fee = fields.Float()
    national_id = fields.Char(translate=True, size=64)
    payed_for_id = fields.Boolean(default=False)
    is_leader = fields.Boolean(string="Is Leader", default=False, required=True)
    leader_responsibility = fields.Many2one('leaders.responsibility')
    leader_sub_responsibility = fields.Many2many('leaders.sub.responsibility', string="Leader's Sub Responsibility")
    leader_stock = fields.Selection(selection=[('appointed', 'Appointed'), ('not appointed', 'Not Appointed')], default='not appointed')
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    experience = fields.Char(translate=True, string="Leadership Experience Year", size=64)
    work_experience = fields.Char(translate=True, string="Work Experience Year", size=64)
    payment_method = fields.Selection(selection=[('cash', 'Cash'), ('percentage', 'Percentage')], default="cash", required=True)
    membership_monthly_fee_cash = fields.Float()
    membership_monthly_fee_percent = fields.Float(compute="_compute_according_to_income", store=True)
    membership_monthly_fee_cash_from_percent = fields.Float(store=True, compute="_compute_according_to_income")
    type_of_payment = fields.Selection(selection=[('in person', 'Cash'), ('bank', 'Bank')], default='in person', required=True)
    grade = fields.Selection(selection=[('very high', 'Very High'), ('high', 'High'), ('mid', 'Mid'), ('low', 'Low'), ('very low', 'Very Low')], default='low', required=True)
    key_strength = fields.Many2many('interpersonal.skills', 'positive_skill_import_rel', domain="[('positive', '=', True)]", translate=True)
    key_weakness = fields.Many2many('interpersonal.skills', domain="[('positive', '=', False)]", translate=True)
    supporter_id = fields.Many2one('supporter.members', readonly=True)
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    is_supporter = fields.Boolean(default=False)
    is_candidate = fields.Boolean(default=False)
    new_member = fields.Boolean(default=False)
    state = fields.Selection(selection=[('duplicate_data', 'Duplicated Data'), ('duplicate_phone', 'Duplicated Phone'), ('duplicate_email', 'Duplicated Email'), ('duplicate_national_id', 'Duplicated National ID')])
    member_system_admin = fields.Boolean(default=False)
    leader_system_admin = fields.Boolean(default=False)
    league_system_admin = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        vals['name'] = vals['first_name'] + " " + vals['father_name'] + " " + vals['grand_father_name']
        res = super(ImportationModule, self).create(vals)

        # String Validation
        if res.first_name:
            for st in res.first_name:
                if st.isdigit():
                    raise UserError(_("You Can't Have A Digit in First Name"))

        if res.father_name:
            for st in res.father_name:
                if st.isdigit():
                    raise UserError(_("You Can't Have A Digit in Father's Name"))

        if res.grand_father_name:
            for st in res.grand_father_name:
                if st.isdigit():
                    raise UserError(_("You Can't Have A Digit in Grand Father's Name"))

        if res.position:
            for st in res.position:
                if st.isdigit():
                    raise UserError(_("You Can't Have A Digit in Job Position"))

        # Phone Validation
        if res.phone:
            for st in res.phone:
                if not st.isdigit():
                    raise UserError(_("You Can't Have Characters in a Phone Number"))
            if res.phone[0] != '0':
                raise UserError(_("A Valid Phone Number Starts With 0"))
            if len(res.phone) != 10:
                raise UserError(_("A Valid Phone Number Has 10 Digits"))

        # House Phone Validation
        if res.house_phone_number:
            for st in res.house_phone_number:
                if not st.isdigit():
                    raise UserError(_("You Can't Have Characters in an House Phone Number"))
            if res.house_phone_number[0] != '0':
                raise UserError(_("A Valid House Phone Number Starts With 0"))
            if len(res.house_phone_number) != 10:
                raise UserError(_("A Valid House Phone Number Has 10 Digits"))

        # Office Phone Validation
        if res.office_phone_number:
            for st in res.office_phone_number:
                if not st.isdigit():
                    raise UserError(_("You Can't Have Characters in an Office Phone Number"))
            if res.office_phone_number[0] != '0':
                raise UserError(_("A Valid Office Phone Number Starts With 0"))
            if len(res.office_phone_number) != 10:
                raise UserError(_("A Valid Office Phone Number Has 10 Digits"))

        # Email Validation
        if res.email_address:
            if '@' not in res.email_address or '.' not in res.email_address:
                raise UserError(_("A Valid Email Address has '@' and '.'"))

        # Income Validation
        if res.income:
            if res.income < 0.00:
                raise UserError(_("An Income can't be Negative"))

        # Monthly Fee
        if res.membership_monthly_fee_cash:
            if res.membership_monthly_fee_cash < 0.00:
                raise UserError(_("An Monthly Fee can't be Negative"))

        # League Monthly Fee
        if res.league_payment:
            if res.league_payment < 0.00:
                raise UserError(_("An League Monthly Fee can't be Negative"))

        if res.wereda_id.parent_id.id != res.subcity_id.id:
            raise UserError(_("The Working Woreda Selected %s doesn't belong to Working Subcity %s") % (res.wereda_id.name, res.subcity_id.name))

        if res.main_office.wereda_id.id != res.wereda_id.id and (res.is_member or res.is_leader):
            raise UserError(_("The Member Basic Organization Selected %s doesn't belong to the Working Woreda %s") % (res.main_office.name, res.wereda_id.name))

        if res.league_main_office.wereda_id.id != res.wereda_id.id and (res.is_league):
            raise UserError(_("The League Basic Organization Selected %s doesn't belong to the Working Woreda %s") % (res.league_main_office.name, res.wereda_id.name))

        if res.league_member_cells.main_office.id != res.league_main_office.id and (res.is_league):
            raise UserError(_("The League Cell selected %s doesn't belong to The League Basic Organization %s") % (res.league_member_cells.name, res.league_main_office.name))

        if res.member_cells.main_office.id != res.main_office.id and (res.is_member or res.is_leader):
            raise UserError(_("The Member Cell selected %s doesn't belong to The Member Basic Organization %s") % (res.member_cells.name, res.main_office.name))

        if res.league_organization.id != res.league_main_office.member_main_type_id.id and (res.is_league):
            raise UserError(_("The Type of League Organization selected %s is not of The Type of Organization of the League Basic Organization %s") % (res.league_organization.name, res.league_main_office.member_main_type_id.name))

        if res.membership_org.id != res.main_office.member_main_type_id.id and (res.is_member or res.is_leader):
            raise UserError(_("The Type of Member Organization selected %s is not of The Type of Organization of the Member Basic Organization %s") % (res.membership_org.name, res.main_office.member_main_type_id.name))

        if res.league_organization.id != res.league_member_cells.member_cell_type_id.id and (res.is_league):
            raise UserError(_("The Type of League Organization selected %s is not of The Type of Organization of the League Cell %s") % (res.league_organization.name, res.league_member_cells.member_cell_type_id.name))

        if res.membership_org.id != res.member_cells.member_cell_type_id.id and (res.is_member or res.is_leader):
            raise UserError(_("The Type of Member Organization selected %s is not of The Type of Organization of the Member Cell %s") % (res.membership_org.name, res.member_cells.member_cell_type_id.name))

        if res.membership_monthly_fee_cash == 0.00 and res.payment_method == 'percentage' and res.income == 0.00:
            raise UserError(_("Please Add Cash Amount for %s if Their income is to be Computed from Percentage") % (res.name))
        return res


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'age' in fields:
            fields.remove('age')
        return super(ImportationModule, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)


    def unlink(self):
        """This function will not delete imported files"""
        for record in self:
            raise UserError(_("Imported Members Aren't Allowed to Be Deleted Only Modified."))
        return super(ImportationModule, self).unlink()


    @api.onchange("leader_responsibility")
    def _chnage_domain_sub_responsibility(self):
        """This function will chnage the sub responsibility based on leader responsibility"""
        for record in self:
            if record.leader_responsibility and record.leader_responsibility.id == 1:
                return {'domain': {'leader_sub_responsibility': [('total_in_woreda', '>', 0)]}}
            if record.leader_responsibility and record.leader_responsibility.id == 2:
                return {'domain': {'leader_sub_responsibility': [('total_in_subcity', '>', 0)]}}
            if record.leader_responsibility and record.leader_responsibility.id == 3:
                return {'domain': {'leader_sub_responsibility': [('total_in_city', '>', 0)]}}

    @api.depends('date')
    def _chnage_age(self):
        """This function will change the age of person based on date"""
        for record in self:
            if record.date:
                today = date.today()
                if record.date >= today:
                    raise UserError(_("You Have To Pick A Date Before Today."))
                if today.month < record.date.month:
                    record.age = (today.year - record.date.year) - 1
                    if record.age == 0:
                        raise UserError(_("Please Add The Appropriate Age for The Individual"))
                else:
                    if today.month == record.date.month and today.day < record.date.day:
                        record.age = (today.year - record.date.year) - 1
                        if record.age == 0:
                            raise UserError(_("Please Add The Appropriate Age for The Individual"))
                    else:
                        record.age = today.year - record.date.year
                        if record.age == 0:
                            raise UserError(_("Please Add The Appropriate Age for The Individual"))


    @api.depends('income', 'membership_monthly_fee_cash', 'payment_method')
    def _compute_according_to_income(self):
        """This will compute methods of payments based on your income"""
        for record in self:
            if record.income < 0.00:
                raise UserError(_("Income Can't Be Negative"))
            elif record.income > 0.00:
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
            else:
                if record.payment_method == 'percentage':
                    if record.membership_monthly_fee_cash == 0.00:
                        raise UserError(_("Please Add Cash Amount for %s if Their income is to be Computed from Percentage") % (record.name))
                    elif record.membership_monthly_fee_cash < 0.00:
                        raise UserError(_("Cash Can't Be Negative"))
                    elif record.membership_monthly_fee_cash != 0.00:
                        all_fee = self.env['payment.fee.configuration'].search([])
                        if all_fee:
                            for fee in all_fee:
                                minimum = fee.minimum_wage * (fee.fee_in_percent / 100)
                                maximum = fee.maximum_wage * (fee.fee_in_percent / 100)
                                if minimum <= record.membership_monthly_fee_cash <= maximum:
                                    record.income = (record.membership_monthly_fee_cash) / (fee.fee_in_percent / 100)
                                    record.membership_monthly_fee_percent = fee.fee_in_percent
                                    record.membership_monthly_fee_cash_from_percent = record.membership_monthly_fee_cash
                                    record.membership_monthly_fee_cash = 0.00
                                    break
                                else:
                                    continue
                        else:
                            raise UserError(_("Please Corrected The Membership Fee from Income Configuration."))  



    @api.depends('payment_method')
    def _change_payment_method(self):
        """This function will change values based on payment methosd"""
        for record in self:
            if record.payment_method == 'cash':
                record.membership_monthly_fee_percent = 0.00
                record.membership_monthly_fee_cash_from_percent = 0.00
            else:
                record.membership_monthly_fee_cash = 0.00

    @api.onchange('subcity_id')
    def _change_all_field_for_supporter(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False
                    record.main_office = False
                    record.member_cells = False
                    record.league_main_office = False
                    record.league_member_cells = False

    # @api.onchange('residential_subcity_id')
    # def _change_all_field_for_supporter_residential(self):
    #     """This function will make all fields False when subcity changes"""
    #     for record in self:
    #         if record.residential_subcity_id:
    #             if record.residential_subcity_id.id != record.residential_wereda_id.parent_id.id:
    #                 record.residential_wereda_id = False

    @api.onchange('membership_org')
    def _change_membership_org(self):
        """This function will change member organization"""
        for record in self:
            if record.membership_org:
                record.main_office = False
                record.member_cells = False

    @api.onchange('league_organization')
    def _change_league_organization(self):
        """This function will change member organization"""
        for record in self:
            if record.league_organization:
                record.league_main_office = False
                record.league_member_cells = False


    def create_supporter(self):
        """This function will create supporter"""
        for record in self:
            if record.is_supporter or record.is_candidate or record.new_member:
                raise UserError(_("There are Individuals Who Are Already Imported as Supporters, Select the Black Ones to Create Supporters"))

            phone_exists = self.env['supporter.members'].search([('phone', '=', record.phone)])
            exists = self.env['supporter.members'].search([('name', '=', record.name), ('gender', '=', record.gender), ('date', '=', record.date)])
            if phone_exists:
                record.state = 'duplicate_phone'
            elif exists:
                record.state = 'duplicate_data'
            else:
                supporter = self.env['supporter.members'].create({
                    'name': record.name,
                    'first_name': record.first_name,
                    'father_name': record.father_name,
                    'grand_father_name': record.grand_father_name,
                    'date': record.date,
                    'age': record.age,
                    'gender': record.gender,
                    'ethnic_group':  record.ethnic_group.id,
                    'education_level': record.education_level.id,
                    'field_of_study_id': record.field_of_study_id.id,
                    'work_place': record.work_place,
                    'position': record.position,
                    'income': record.income,
                    'subcity_id': record.subcity_id.id,
                    'wereda_id': record.wereda_id.id,
                    'residential_subcity': record.residential_subcity,
                    'residential_wereda': record.residential_wereda,
                    'house_number':record.house_number,
                    'educational_history': record.educational_history.ids,
                    'phone': record.phone,
                    'status': record.status,
                    'gov_responsibility': record.gov_responsibility,
                    'start_of_support': record.start_of_support,
                    'state':  'approved',
                    'email_address': record.email_address,
                    'is_user_input': record.is_user_input,
                    'user_input': record.user_input,
                    'saved': True,
                })

                if record.league_main_office and record.league_member_cells:
                    supporter.write({
                        'main_office_id': record.league_main_office.id,
                        'cell_id': record.league_member_cells.id,
                    })

                if record.main_office and record.member_cells:
                    supporter.write({
                        'main_office_id': record.main_office.id,
                        'cell_id': record.member_cells.id,
                    })

                record.supporter_id = supporter.id
                record.is_supporter = True



    def create_candidate(self):
        """This function will create supporter"""
        for record in self:
            if not record.is_supporter:
                raise UserError(_("There are Individuals Who didn't Become Supporter First, Select the Yellow ones To Create Candidates"))
            if record.is_candidate or record.new_member:
                raise UserError(_("There are Individuals Who Are Already Imported as Candidates, Select the Yellow ones To Create Candidates"))

            phone_exists = self.env['candidate.members'].search([('phone', '=', record.phone)])
            exists = self.env['candidate.members'].search([('name', '=', record.name), ('gender', '=', record.gender), ('date', '=', record.date)])
            if phone_exists:
                record.state = 'duplicate_phone'
            elif exists:
                record.state = 'duplicate_data'
            else:
                candidate = self.env['candidate.members'].create({
                    'name': record.name,
                    'first_name': record.first_name,
                    'father_name': record.father_name,
                    'grand_father_name': record.grand_father_name,
                    'date': record.date,
                    'age': record.age,
                    'gender': record.gender,
                    'ethnic_group':  record.ethnic_group.id,
                    'education_level': record.education_level.id,
                    'field_of_study_id': record.field_of_study_id.id,
                    'source_of_livelihood': record.source_of_livelihood,
                    'income': record.income,
                    'subcity_id': record.subcity_id.id,
                    'wereda_id': record.wereda_id.id,
                    'residential_subcity': record.residential_subcity,
                    'residential_wereda': record.residential_wereda,
                    'house_number':record.house_number,
                    'work_experience_ids': record.work_experience_ids.ids,
                    'educational_history': record.educational_history.ids,
                    'phone': record.phone,
                    'office_phone_number': record.office_phone_number,
                    'house_phone_number': record.house_phone_number,
                    'state':  'approved',
                    'email_address': record.email_address,
                    'is_user_input': record.is_user_input,
                    'user_input': record.user_input,
                    'saved': True,
                    'supporter_id': record.supporter_id.id
                })

                if record.league_main_office and record.league_member_cells:
                    candidate.write({
                        'main_office_id': record.league_main_office.id,
                        'cell_id': record.league_member_cells.id,
                    })

                if record.main_office and record.member_cells:
                    candidate.write({
                        'main_office_id': record.main_office.id,
                        'cell_id': record.member_cells.id,
                    })

                if record.work_place and record.position:
                    candidate.write({
                        'work_experience_ids': [(0, 0, {
                            'name': record.position,
                            'place_of_work': record.work_place,
                            'current_job': True
                        })],
                    })

                record.supporter_id.candidate_id = candidate.id
                record.candidate_id = candidate.id
                record.is_candidate = True
                record.is_supporter = False

    def create_member(self):
        """This function will create supporter"""
        for record in self:
            partner = False
            if (not record.is_league and not record.is_member and not record.is_leader):
                raise UserError(_("%s Can't Become A League, Member or Leader. The Imported Data doesn't Have Enough Information.") % (record.name))
            if record.is_supporter or not record.is_candidate:
                raise UserError(_("There are Individuals Who didn't Become Candidate First, Select the Red ones To Create Members"))
            if record.new_member:
                raise UserError(_("There are Individuals Who are Already Imported as Members, Select the Red ones To Create Members"))
            if record.national_id:
                all_partner = self.env['res.partner'].search([('national_id', '=', record.national_id)])
                if all_partner:
                    record.state = 'duplicate_national_id'
                else:
                    partner = self.member_creation(record)
                    if partner:
                        record.candidate_id.partner_id = partner.id
                        record.partner_id = partner.id
                        record.is_candidate = False
                        record.is_supporter = False
                        record.new_member = True
            else:
                if partner:
                    record.candidate_id.partner_id = partner.id
                    record.partner_id = partner.id
                    record.is_candidate = False
                    record.is_supporter = False
                    record.new_member = True


    def make_partner(self, record):
        """This function will create Partner"""
        partner = self.env['res.partner'].create({
            'name': record.name,
            'first_name': record.first_name,
            'father_name': record.father_name,
            'grand_father_name': record.grand_father_name,
            'date': record.date,
            'age': record.age,
            'gender': record.gender,
            'ethnic_group':  record.ethnic_group.id,
            'education_level': record.education_level.id,
            'field_of_study_id': record.field_of_study_id.id,
            'region_of_birth': record.region_of_birth.id,
            'zone_city_of_birth': record.zone_city_of_birth,
            'wereda_of_birth': record.wereda_of_birth,
            'income': record.income,
            'subcity_id': record.subcity_id.id,
            'wereda_id': record.wereda_id.id,
            'region': record.region.id,
            'residential_subcity': record.residential_subcity,
            'residential_wereda': record.residential_wereda,
            'house_number':record.house_number,
            'kebele': record.kebele,
            'work_experience_ids': record.candidate_id.work_experience_ids.ids,
            'educational_history': record.educational_history.ids,
            'phone': record.phone,
            'email_address': record.email_address,
            'is_user_input': record.is_user_input,
            'user_input': record.user_input,
            'supporter_id': record.supporter_id.id,
            'gov_responsibility': record.gov_responsibility,
            'candidate_id': record.candidate_id.id,
            'supporter_id': record.supporter_id.id,
        })
        return partner

    def member_creation(self, record):
        """This function will create members"""
        role_city = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_city_admin').id])])
        if not role_city:
            raise UserError(_("Please Create a Role for Member City Administrator"))
        role_subcity = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_admin').id])])
        if not role_subcity:
            raise UserError(_("Please Create a Role for Member SubCity Administrator"))
        role_woreda = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_manager').id])])
        if not role_woreda:
            raise UserError(_("Please Create a Role for Member Woreda Administrator"))
        role_basic_manager = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_main_manager').id])])
        if not role_basic_manager:
            raise UserError(_("Please Create a Role for Member Basic Office Administrator"))
        role_basic_assembler = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_main_assembler').id])])
        if not role_basic_assembler:
            raise UserError(_("Please Create a Role for Member Basic Office Assembler"))
        role_basic_finance = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_main_finance').id])])
        if not role_basic_finance:
            raise UserError(_("Please Create a Role for Member Basic Office Finance"))
        role_cell_admin = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_cell_manager').id])])
        if not role_cell_admin:
            raise UserError(_("Please Create a Role for Member Cell Administrator"))
        role_cell_assembler = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_assembler').id])])
        if not role_cell_assembler:
            raise UserError(_("Please Create a Role for Member Cell Assembler"))
        role_cell_finance = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_finance').id])])
        if not role_cell_finance:
            raise UserError(_("Please Create a Role for Member Cell Finance"))
        role_portal = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('base.group_portal').id])])
        if not role_portal:
            raise UserError(_("Please Create a Role for Portal User"))
        role_internal = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('base.group_user').id])])
        if not role_portal:
            raise UserError(_("Please Create a Role for Internal User"))
        partner = False
        if record.email_address:
            existing = self.env['res.users'].sudo().search([('login', '=', record.email_address)])
            if existing:
                record.state = 'duplicate_email'
            else:
                partner = self.make_partner(record)
                partner.user_name = partner.email_address
                partner.has_user_name = True
                user = self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': partner.email_address,
                    'password': '12345678',
                })
                user.write({
                    'role_line_ids': [
                        (
                            0,
                            0,
                            {
                                'role_id': role_portal.id,
                                'user_id': user.id
                            },
                        ),
                    ]
                })
        else:
            partner = self.make_partner(record)
            name = partner.name.split()[0] + partner.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = partner.name.split()[0] + partner.phone[-9:]
                partner.user_name = name
                partner.has_user_name = True
                user = self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '12345678',
                })
                user.write({
                    'role_line_ids': [
                        (
                            0,
                            0,
                            {
                                'role_id': role_portal.id,
                                'user_id': user.id
                            },
                        ),
                    ]
                })
            else:
                partner.user_name = name
                partner.has_user_name = True
                user = self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '12345678',
                })
                user.write({
                    'role_line_ids': [
                        (
                            0,
                            0,
                            {
                                'role_id': role_portal.id,
                                'user_id': user.id,
                            },
                        ),
                    ]
                })

        if partner:
            if partner.gender == 'Female':
                partner.is_woman = True

            code = self.env['ir.sequence'].next_by_code('res.partner')
            new = code[4:]
            ids = "AAPP/" + str(new) + "/" + str(partner.subcity_id.unique_representation_code)  + "/" + str(partner.wereda_id.unique_representation_code)
            partner.member_ids = ids

            if record.is_league and not record.is_member:
                partner.write({
                    'is_league': True,
                    'league_type': record.league_type,
                    'league_organization': record.league_organization.id,
                    'league_responsibility': record.league_responsibility.id,
                    'league_sub_responsibility': record.league_sub_responsibility.id,
                    'start_of_league': record.start_of_league,
                    'grade': record.grade,
                    'key_strength': record.key_strength.ids,
                    'key_weakness': record.key_weakness.ids,
                    'type_of_payment': record.type_of_payment,
                    'league_main_office': record.league_main_office.id,
                    'league_member_cells': record.league_member_cells.id,
                    'was_league': True,
                    'was_supporter': True,
                    'was_candidate': True,
                    'pay_for_league': record.pay_for_league,
                    'league_payment': record.league_payment,
                    'track_league_fee': record.track_league_fee,
                })


                if record.league_system_admin:
                    all_leagues = partner.league_member_cells.leagues_ids.ids + [partner.id]
                    all_league_leaders = partner.league_member_cells.league_leaders_ids.ids + [partner.id]
                    if partner.league_responsibility.id == 1:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.league_sub_responsibility.id == 1: # Cell Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                        elif partner.league_sub_responsibility.id == 2: # Cell Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                        elif partner.league_sub_responsibility.id == 3: # Main Office Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                        elif partner.league_sub_responsibility.id == 4: # Main Office Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                        else:
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]

                    if partner.league_responsibility.id == 2:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.league_sub_responsibility.id == 1: # Cell Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                        elif partner.league_sub_responsibility.id == 2: # Cell Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                        else:
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]

                    if partner.league_responsibility.id == 3:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.league_sub_responsibility.id == 3: # Main Office Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                        elif partner.league_sub_responsibility.id == 4: # Main Office Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                        else:
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                else:
                    all_leagues = partner.league_member_cells.leagues_ids.ids + [partner.id]
                    all_league_leaders = partner.league_member_cells.league_leaders_ids.ids + [partner.id]
                    if partner.league_responsibility.id == 1:
                        all_leagues = partner.league_member_cells.leagues_ids.ids + [partner.id]
                        partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                        partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]

            if record.is_member and record.is_league:
                partner.write({
                    'is_member': True,
                    'is_league': True,
                    'league_type': record.league_type,
                    'membership_org': record.membership_org.id,
                    'league_organization': record.league_organization.id,
                    'member_responsibility': record.member_responsibility.id,
                    'league_responsibility': record.league_responsibility.id,
                    'member_sub_responsibility': record.member_sub_responsibility.id,
                    'league_sub_responsibility': record.league_sub_responsibility.id,
                    'start_of_membership': record.start_of_membership,
                    'grade': record.grade,
                    'key_strength': record.key_strength.ids,
                    'key_weakness': record.key_weakness.ids,
                    'type_of_payment': record.type_of_payment,
                    'main_office': record.league_main_office.main_office_id.id,
                    'member_cells': record.league_member_cells.cell_id.id,
                    'league_main_office': record.league_main_office.id,
                    'league_member_cells': record.league_member_cells.id,
                    'was_member': True,
                    'was_league': True,
                    'was_supporter': True,
                    'was_candidate': True,
                    'payment_method': record.payment_method,
                    'membership_monthly_fee_cash': record.membership_monthly_fee_cash,
                    'membership_monthly_fee_cash_from_percent': record.membership_monthly_fee_cash_from_percent,
                    'membership_monthly_fee_percent': record.membership_monthly_fee_percent,
                    'track_member_fee': record.track_member_fee,
                    'pay_for_league': record.pay_for_league,
                    'league_payment': record.league_payment,
                    'track_league_fee': record.track_league_fee,
                    'stock': record.stock,
                    'work_experience': record.work_experience,
                    'national_id': record.national_id,
                })


                if record.league_system_admin:
                    all_leagues = partner.league_member_cells.leagues_ids.ids + [partner.id]
                    all_league_leaders = partner.league_member_cells.league_leaders_ids.ids + [partner.id]
                    if partner.league_responsibility.id == 1:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.league_sub_responsibility.id == 1: # Cell Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                            partner.league_member_cells.cell_id.leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.leaders_ids = [(6, 0, all_league_leaders)]
                        elif partner.league_sub_responsibility.id == 2: # Cell Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                            partner.league_member_cells.cell_id.leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.leaders_ids = [(6, 0, all_league_leaders)]
                        elif partner.league_sub_responsibility.id == 3: # Main Office Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                            partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)]
                        elif partner.league_sub_responsibility.id == 4: # Main Office Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                            partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)]
                        else:
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                            partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)]

                    if partner.league_responsibility.id == 2:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.league_sub_responsibility.id == 1: # Cell Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                            partner.league_member_cells.cell_id.leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.leaders_ids = [(6, 0, all_league_leaders)]
                        elif partner.league_sub_responsibility.id == 2: # Cell Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                            partner.league_member_cells.cell_id.leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.leaders_ids = [(6, 0, all_league_leaders)]
                        else:
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.league_leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.league_leaders_ids = [(6, 0, all_league_leaders)]
                            partner.league_member_cells.cell_id.leaders_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.leaders_ids = [(6, 0, all_league_leaders)]

                    if partner.league_responsibility.id == 3:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.league_sub_responsibility.id == 3: # Main Office Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                            partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)]
                        elif partner.league_sub_responsibility.id == 4: # Main Office Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                            partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)]
                        else:
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                            partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                            partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                            partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)]
                else:
                    all_leagues = partner.league_member_cells.leagues_ids.ids + [partner.id]
                    all_league_leaders = partner.league_member_cells.league_leaders_ids.ids + [partner.id]
                    if partner.league_responsibility.id == 1:
                        partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                        partner.league_member_cells.leagues_ids = [(6, 0, all_leagues)]
                        partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                        partner.league_member_cells.cell_id.members_ids = [(6, 0, all_leagues)] 


            if record.is_member and not record.is_league:
                partner.write({
                    'is_member': True,
                    'membership_org': record.membership_org.id,
                    'member_responsibility': record.member_responsibility.id,
                    'member_sub_responsibility': record.member_sub_responsibility.id,
                    'start_of_membership': record.start_of_membership,
                    'grade': record.grade,
                    'key_strength': record.key_strength.ids,
                    'key_weakness': record.key_weakness.ids,
                    'type_of_payment': record.type_of_payment,
                    'main_office': record.main_office.id,
                    'member_cells': record.member_cells.id,
                    'was_member': True,
                    'was_supporter': True,
                    'was_candidate': True,
                    'payment_method': record.payment_method,
                    'membership_monthly_fee_cash': record.membership_monthly_fee_cash,
                    'membership_monthly_fee_cash_from_percent': record.membership_monthly_fee_cash_from_percent,
                    'membership_monthly_fee_percent': record.membership_monthly_fee_percent,
                    'track_member_fee': record.track_member_fee,
                    'stock': record.stock,
                    'work_experience': record.work_experience,
                    'national_id': record.national_id,
                }) 

                if record.member_system_admin:
                    all_members = partner.member_cells.members_ids.ids + [partner.id]
                    all_leaders = partner.member_cells.leaders_ids.ids + [partner.id]
                    if partner.member_responsibility.id == 1:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.member_sub_responsibility.id == 1: # Cell Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.leaders_ids = [(5, 0, 0)]
                            partner.member_cells.leaders_ids = [(6, 0, all_leaders)]
                        elif partner.member_sub_responsibility.id == 2: # Cell Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.leaders_ids = [(5, 0, 0)]
                            partner.member_cells.leaders_ids = [(6, 0, all_leaders)]
                        elif partner.member_sub_responsibility.id == 3: # Main Office Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.members_ids = [(5, 0, 0)]
                            partner.member_cells.members_ids = [(6, 0, all_members)]
                        elif partner.member_sub_responsibility.id == 4: # Main Office Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.members_ids = [(5, 0, 0)]
                            partner.member_cells.members_ids = [(6, 0, all_members)]
                        else:
                            partner.member_cells.members_ids = [(5, 0, 0)]
                            partner.member_cells.members_ids = [(6, 0, all_members)]

                    if partner.member_responsibility.id == 2:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.member_sub_responsibility.id == 1: # Cell Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.leaders_ids = [(5, 0, 0)]
                            partner.member_cells.leaders_ids = [(6, 0, all_leaders)]
                        elif partner.member_sub_responsibility.id == 2: # Cell Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.leaders_ids = [(5, 0, 0)]
                            partner.member_cells.leaders_ids = [(6, 0, all_leaders)]
                        else:
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_cell_admin.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.leaders_ids = [(5, 0, 0)]
                            partner.member_cells.leaders_ids = [(6, 0, all_leaders)]

                    if partner.member_responsibility.id == 3:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if partner.member_sub_responsibility.id == 3: # Main Office Finance
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_finance.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.members_ids = [(5, 0, 0)]
                            partner.member_cells.members_ids = [(6, 0, all_members)]
                        elif partner.member_sub_responsibility.id == 4: # Main Office Assembler
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_assembler.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.members_ids = [(5, 0, 0)]
                            partner.member_cells.members_ids = [(6, 0, all_members)]
                        else:
                            if user:
                                remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                                user.write({
                                    'role_line_ids': [(3, remove.id)]
                                })
                                user.write({
                                    'role_line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'role_id': role_basic_manager.id,
                                            'user_id': user.id,
                                        },
                                    ),
                                    (
                                        0, 
                                        0,
                                        {
                                            'role_id': role_internal.id,
                                            'user_id': user.id,
                                        },                                   
                                    )
                                    ]
                                })
                            partner.member_cells.members_ids = [(5, 0, 0)]
                            partner.member_cells.members_ids = [(6, 0, all_members)]
                else:
                    all_members = partner.member_cells.members_ids.ids + [partner.id]
                    all_leaders = partner.member_cells.leaders_ids.ids + [partner.id]
                    if partner.member_responsibility.id == 1:
                        partner.member_cells.members_ids = [(5, 0, 0)]
                        partner.member_cells.members_ids = [(6, 0, all_members)]


            if record.is_leader and record.is_league:
                partner.write({
                    'is_leader': True,
                    'is_league': True,
                    'league_type': record.league_type,
                    'membership_org': record.membership_org.id,
                    'league_organization': record.league_organization.id,
                    'leader_responsibility': record.leader_responsibility.id,
                    'league_responsibility': record.league_responsibility.id,
                    'league_sub_responsibility': record.league_sub_responsibility.id,
                    'start_of_membership': record.start_of_membership,
                    'grade': record.grade,
                    'key_strength': record.key_strength.ids,
                    'key_weakness': record.key_weakness.ids,
                    'type_of_payment': record.type_of_payment,
                    'main_office': record.league_main_office.main_office_id.id,
                    'member_cells': record.league_member_cells.cell_id.id,
                    'league_main_office': record.league_main_office.id,
                    'league_member_cells': record.league_member_cells.id,
                    'was_member': True,
                    'was_league': True,
                    'was_supporter': True,
                    'was_candidate': True,
                    'payment_method': record.payment_method,
                    'membership_monthly_fee_cash': record.membership_monthly_fee_cash,
                    'membership_monthly_fee_cash_from_percent': record.membership_monthly_fee_cash_from_percent,
                    'membership_monthly_fee_percent': record.membership_monthly_fee_percent,
                    'track_member_fee': record.track_member_fee,
                    'pay_for_league': record.pay_for_league,
                    'league_payment': record.league_payment,
                    'track_league_fee': record.track_league_fee,
                    'leader_stock': record.leader_stock,
                    'leadership_status': record.leadership_status,
                    'experience': record.experience,
                    'work_experience': record.work_experience,
                    'national_id': record.national_id,
                })


                all_members = partner.member_cells.members_ids.ids + [partner.id]
                all_league_members = partner.league_member_cells.leagues_ids.ids + [partner.id]
                partner.member_cells.members_ids = [(5, 0, 0)]
                partner.member_cells.members_ids = [(6, 0, all_members)]
                partner.league_member_cells.leagues_ids = [(5, 0, 0)]
                partner.league_member_cells.leagues_ids = [(6, 0, all_league_members)]
                partner.league_member_cells.cell_id.members_ids = [(5, 0, 0)]
                partner.league_member_cells.cell_id.members_ids = [(6, 0, all_league_members)]

                sub_responsibility = self.env['leaders.sub.responsibility'].search([])

                user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                if partner.leader_responsibility.id == 1:
                    if user and record.leader_system_admin:
                        remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                        user.write({
                            'role_line_ids': [(3, remove.id)]
                        })
                        user.write({
                            'role_line_ids': [
                            (
                                0,
                                0,
                                {
                                    'role_id': role_woreda.id,
                                    'user_id': user.id,
                                },
                            ),
                            (
                                0, 
                                0,
                                {
                                    'role_id': role_internal.id,
                                    'user_id': user.id,
                                },                                   
                            )
                            ]
                        })
                        all_woreda_admin = partner.wereda_id.branch_manager.ids + [user.id]
                        partner.wereda_id.branch_manager = [(5, 0, 0)]
                        partner.wereda_id.branch_manager = [(6, 0, all_woreda_admin)]
                        partner.subcity_admin = False
                        partner.city_admin = False

                    for sub in sub_responsibility:
                        if sub.id in record.leader_sub_responsibility.ids:
                            woreda_exists = self.env['res.partner'].search([('leader_sub_responsibility', 'in', sub.id), ('leader_responsibility', '=', record.leader_responsibility.id), ('wereda_id', '=', record.wereda_id.id)])
                            if len(woreda_exists.ids) < sub.total_in_woreda or not woreda_exists:
                                all_sub = partner.leader_sub_responsibility.ids + [sub.id]
                                partner.write({
                                    'leader_sub_responsibility': [(5, 0, 0)]
                                })
                                partner.write({
                                    'leader_sub_responsibility': [(6, 0, all_sub)]
                                })
                            else:
                                raise UserError(_("%s can't be %s. The Woreda %s has already enough %s.") % (record.name, sub.name, record.wereda_id.name, sub.name))

                if partner.leader_responsibility.id == 2:
                    if user and record.leader_system_admin:
                        remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                        user.write({
                            'role_line_ids': [(3, remove.id)]
                        })
                        user.write({
                            'role_line_ids': [
                            (
                                0,
                                0,
                                {
                                    'role_id': role_subcity.id,
                                    'user_id': user.id,
                                },
                            ),
                            (
                                0, 
                                0,
                                {
                                    'role_id': role_internal.id,
                                    'user_id': user.id,
                                },                                   
                            )
                            ]
                        })
                        all_subcity_admin = partner.subcity_id.parent_manager.ids + [user.id]
                        partner.subcity_id.parent_manager = [(5, 0, 0)]
                        partner.subcity_id.parent_manager = [(6, 0, all_subcity_admin)]
                        partner.subcity_admin = True
                        partner.city_admin = False

                    for sub in sub_responsibility:
                        if sub.id in record.leader_sub_responsibility.ids:
                            subcity_exists = self.env['res.partner'].search([('leader_sub_responsibility', 'in', sub.id), ('leader_responsibility', '=', record.leader_responsibility.id), ('subcity_id', '=', record.subcity_id.id)])
                            if len(subcity_exists.ids) < sub.total_in_subcity or not subcity_exists:
                                all_sub = partner.leader_sub_responsibility.ids + [sub.id]
                                partner.write({
                                    'leader_sub_responsibility': [(5, 0, 0)]
                                })
                                partner.write({
                                    'leader_sub_responsibility': [(6, 0, all_sub)]
                                })
                            else:
                                raise UserError(_("%s can't be %s. The Subcity %s has already enough %s.") % (record.name, sub.name, record.subcity_id.name, sub.name))

                if partner.leader_responsibility.id == 3:
                    if user and record.leader_system_admin:
                        remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                        user.write({
                            'role_line_ids': [(3, remove.id)]
                        })
                        user.write({
                            'role_line_ids': [
                            (
                                0,
                                0,
                                {
                                    'role_id': role_city.id,
                                    'user_id': user.id,
                                },
                            ),
                            (
                                0, 
                                0,
                                {
                                    'role_id': role_internal.id,
                                    'user_id': user.id,
                                },                                   
                            )
                            ]
                        })
                        all_city_admin = partner.subcity_id.city_id.city_manager.ids + [user.id]
                        partner.subcity_id.city_id.city_manager = [(5, 0, 0)]
                        partner.subcity_id.city_id.city_manager = [(6, 0, all_city_admin)]
                        partner.subcity_admin = False
                        partner.city_admin = True

                    for sub in sub_responsibility:
                        if sub.id in record.leader_sub_responsibility.ids:
                            city_exists = self.env['res.partner'].search([('leader_sub_responsibility', 'in', sub.id)], ('leader_responsibility', '=', record.leader_responsibility.id))
                            if len(city_exists.ids) < sub.total_in_city or not city_exists:
                                all_sub = partner.leader_sub_responsibility.ids + [sub.id]
                                partner.write({
                                    'leader_sub_responsibility': [(5, 0, 0)]
                                })
                                partner.write({
                                    'leader_sub_responsibility': [(6, 0, all_sub)]
                                })
                            else:
                                raise UserError(_("%s can't be %s. The City %s has already enough %s.") % (record.name, sub.name, record.city_id.name, sub.name))




            if record.is_leader and not record.is_league:
                partner.write({
                    'is_leader': True,
                    'membership_org': record.membership_org.id,
                    'leader_responsibility': record.leader_responsibility.id,
                    'leader_sub_responsibility': record.leader_sub_responsibility.ids,
                    'start_of_membership': record.start_of_membership,
                    'grade': record.grade,
                    'key_strength': record.key_strength.ids,
                    'key_weakness': record.key_weakness.ids,
                    'type_of_payment': record.type_of_payment,
                    'main_office': record.main_office.id,
                    'member_cells': record.member_cells.id,
                    'was_member': True,
                    'was_supporter': True,
                    'was_candidate': True,
                    'payment_method': record.payment_method,
                    'membership_monthly_fee_cash': record.membership_monthly_fee_cash,
                    'membership_monthly_fee_cash_from_percent': record.membership_monthly_fee_cash_from_percent,
                    'membership_monthly_fee_percent': record.membership_monthly_fee_percent,
                    'track_member_fee': record.track_member_fee,
                    'leader_stock': record.leader_stock,
                    'leadership_status': record.leadership_status,
                    'experience': record.experience,
                    'work_experience': record.work_experience,
                    'national_id': record.national_id,
                }) 

                all_members = partner.member_cells.members_ids.ids + [partner.id]
                partner.member_cells.members_ids = [(5, 0, 0)]
                partner.member_cells.members_ids = [(6, 0, all_members)]


                sub_responsibility = self.env['leaders.sub.responsibility'].search([])

                user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                if partner.leader_responsibility.id == 1:
                    if user and record.leader_system_admin:
                        remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                        user.write({
                            'role_line_ids': [(3, remove.id)]
                        })
                        user.write({
                            'role_line_ids': [
                            (
                                0,
                                0,
                                {
                                    'role_id': role_woreda.id,
                                    'user_id': user.id,
                                },
                            ),
                            (
                                0, 
                                0,
                                {
                                    'role_id': role_internal.id,
                                    'user_id': user.id,
                                },                                   
                            )
                            ]
                        })
                        all_woreda_admin = partner.wereda_id.branch_manager.ids + [user.id]
                        partner.wereda_id.branch_manager = [(5, 0, 0)]
                        partner.wereda_id.branch_manager = [(6, 0, all_woreda_admin)]
                        partner.subcity_admin = False
                        partner.city_admin = False

                    for sub in sub_responsibility:
                        if sub.id in record.leader_sub_responsibility.ids:
                            woreda_exists = self.env['res.partner'].search([('leader_sub_responsibility', 'in', sub.id), ('leader_responsibility', '=', record.leader_responsibility.id), ('wereda_id', '=', record.wereda_id.id)])
                            if len(woreda_exists.ids) < sub.total_in_woreda or not woreda_exists:
                                all_sub = partner.leader_sub_responsibility.ids + [sub.id]
                                partner.write({
                                    'leader_sub_responsibility': [(5, 0, 0)]
                                })
                                partner.write({
                                    'leader_sub_responsibility': [(6, 0, all_sub)]
                                })
                            else:
                                raise UserError(_("%s can't be %s. The Woreda %s has already enough %s.") % (record.name, sub.name, record.wereda_id.name, sub.name))

                if partner.leader_responsibility.id == 2:
                    if user and record.leader_system_admin:
                        remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                        user.write({
                            'role_line_ids': [(3, remove.id)]
                        })
                        user.write({
                            'role_line_ids': [
                            (
                                0,
                                0,
                                {
                                    'role_id': role_subcity.id,
                                    'user_id': user.id,
                                },
                            ),
                            (
                                0, 
                                0,
                                {
                                    'role_id': role_internal.id,
                                    'user_id': user.id,
                                },                                   
                            )
                            ]
                        })
                        all_subcity_admin = partner.subcity_id.parent_manager.ids + [user.id]
                        partner.subcity_id.parent_manager = [(5, 0, 0)]
                        partner.subcity_id.parent_manager = [(6, 0, all_subcity_admin)]
                        partner.subcity_admin = True
                        partner.city_admin = False

                    for sub in sub_responsibility:
                        if sub.id in record.leader_sub_responsibility.ids:
                            subcity_exists = self.env['res.partner'].search([('leader_sub_responsibility', 'in', sub.id), ('leader_responsibility', '=', record.leader_responsibility.id), ('subcity_id', '=', record.subcity_id.id)])
                            if len(subcity_exists.ids) < sub.total_in_subcity or not subcity_exists:
                                all_sub = partner.leader_sub_responsibility.ids + [sub.id]
                                partner.write({
                                    'leader_sub_responsibility': [(5, 0, 0)]
                                })
                                partner.write({
                                    'leader_sub_responsibility': [(6, 0, all_sub)]
                                })
                            else:
                                raise UserError(_("%s can't be %s. The Subcity %s has already enough %s.") % (record.name, sub.name, record.subcity_id.name, sub.name))

                if partner.leader_responsibility.id == 3:
                    if user and record.leader_system_admin:
                        remove = user.role_line_ids.filtered(lambda res: res.role_id.id == role_portal.id)
                        user.write({
                            'role_line_ids': [(3, remove.id)]
                        })
                        user.write({
                            'role_line_ids': [
                            (
                                0,
                                0,
                                {
                                    'role_id': role_city.id,
                                    'user_id': user.id,
                                },
                            ),
                            (
                                0, 
                                0,
                                {
                                    'role_id': role_internal.id,
                                    'user_id': user.id,
                                },                                   
                            )
                            ]
                        })
                        all_city_admin = partner.subcity_id.city_id.city_manager.ids + [user.id]
                        partner.subcity_id.city_id.city_manager = [(5, 0, 0)]
                        partner.subcity_id.city_id.city_manager = [(6, 0, all_city_admin)]
                        partner.subcity_admin = False
                        partner.city_admin = True

                    for sub in sub_responsibility:
                        if sub.id in record.leader_sub_responsibility.ids:
                            city_exists = self.env['res.partner'].search([('leader_sub_responsibility', 'in', sub.id)], ('leader_responsibility', '=', record.leader_responsibility.id))
                            if len(city_exists.ids) < sub.total_in_city or not city_exists:
                                all_sub = partner.leader_sub_responsibility.ids + [sub.id]
                                partner.write({
                                    'leader_sub_responsibility': [(5, 0, 0)]
                                })
                                partner.write({
                                    'leader_sub_responsibility': [(6, 0, all_sub)]
                                })
                            else:
                                raise UserError(_("%s can't be %s. The City %s has already enough %s.") % (record.name, sub.name, record.city_id.name, sub.name))


            return partner
        else:
            return False