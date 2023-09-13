"""This file will deal with the archiving members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
import base64
from dateutil.relativedelta import relativedelta


class SendSupporters(models.TransientModel):
    _name="send.supporters"
    _description="This model will handle the sending of supporters to main office and cells"

    wereda_id = fields.Many2one('membership.handlers.branch')
    supporter_id = fields.Many2one('supporter.members')
    candidate_id = fields.Many2one('candidate.members')
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", string="Basic Organization")
    cells = fields.Many2one('member.cells', domain="[('main_office', '=', main_office)]")


    @api.onchange('main_office')
    def _check_admins(self):
        """This function will check if a cell has a main office administrator"""
        if self.main_office:
            if not self.main_office.main_admin:
                raise UserError(_("The Selected Basic Organization Doesn't Have A Basic Organization Leader"))        

    @api.onchange('cells')
    def _remove_main_office(self):
        """This function will check to make sure main office comes first"""
        if self.cells and not self.main_office:
            self.cells = False
            self.main_office = False
        if self.cells and self.main_office:
            if not self.cells.cell_admin:
                raise UserError(_("The Selected Cell Doesn't Have A Cell Leader"))

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['send.supporters'].search([('id', '=', self.id)])
        user = self.env.user
        # if wizard.supporter_id:
        if self.main_office and self.cells:
            wizard.supporter_id.write({
                'main_office_id': self.main_office.id,
                'cell_id': self.cells.id,
                'name': wizard.supporter_id.first_name + " " + wizard.supporter_id.father_name + " " + wizard.supporter_id.grand_father_name,
                'becomes_a_candidate_on': date.today() + relativedelta(months=3),
                'saved': True,
                'state': 'new',
            })
            mail_temp = self.env.ref('supporter_acceptance')
            mail_temp.send_mail(wizard.supporter_id.id)
            all_supporters = self.cells.supporter_ids.ids + [wizard.supporter_id.id]
            self.cells.supporter_ids= [(5, 0, 0)]
            self.cells.supporter_ids = [(6, 0, all_supporters)]
        else:
            raise UserError(_("Please Fill In The Given Informations"))
        message = _("Supporter Has Been Approved")
        title =_("<h4>Supporter Approved</h4>")
        user.notify_success(message, title, True)

class ArchiveMembers(models.TransientModel):
    _name="archive.members.wizard"
    _description="This model will handle the archiving members"

    member_id = fields.Many2one('res.partner')
    is_leader = fields.Boolean(related="member_id.is_leader")
    is_member = fields.Boolean(related="member_id.is_member")
    demote_to = fields.Selection(selection=[('member', 'Member'), ('candidate', 'Candidate'), ('supporter', 'Supporter')], default='member')
    departure_reason = fields.Selection(selection=[('fired', 'Fired'),  ('demote', 'Demote'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        if self.departure_reason and self.additional_information and self.demote_to :
            archive = self.env['archived.information'].sudo().create({
                'member_id': self.member_id.id,
                'date_from': date.today(),
                'departure_reason': self.departure_reason,
                'additional_information': self.additional_information,
                'archived': True
            })
            if self.departure_reason == 'resigned' or self.departure_reason == 'retired' or self.departure_reason == 'death' or self.departure_reason == 'fired':
                user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                user.write({
                    'active': False
                })
                self.member_id.candidate_id.active = False
                self.member_id.supporter_id.active = False
                self.member_id.active = False
            if self.departure_reason == 'demote' and self.is_leader == False and self.demote_to == 'member':
                raise UserError(_("Only Leaders Can Be Demoted to Member"))
            if self.departure_reason == 'demote' and self.is_leader == True:
                if self.demote_to == 'member':
                    self.member_id.is_leader = False
                    self.member_id.is_member = True
                    self.member_id.demote = True
                if self.demote_to == 'candidate':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.active = False
                if self.demote_to == 'supporter':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.candidate_id.active = False
                    self.member_id.active = False
            if self.departure_reason == 'demote' and (self.is_member == True or self.member_id.is_league == True):
                if self.demote_to == 'candidate':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.active = False
                if self.demote_to == 'supporter':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.candidate_id.active = False
                    self.member_id.active = False
        else:
            raise UserError(_("Please Fill In The Given Informations"))

class ArchiveCandidate(models.TransientModel):
    _name="archive.candidate.wizard"
    _description="This model will handle the archiving of members"

    candidate_id = fields.Many2one('candidate.members')
    departure_reason = fields.Selection(selection=[('fired', 'Fired'),  ('demote', 'Demote'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        if self.departure_reason and self.additional_information:
            archive = self.env['archived.information'].sudo().create({
                'candidate_id': self.candidate_id.id,
                'date_from': date.today(),
                'departure_reason': self.departure_reason,
                'additional_information': self.additional_information,
                'archived': True
            })
            if self.departure_reason == 'resigned' or self.departure_reason == 'retired' or self.departure_reason == 'death' or self.departure_reason == 'fired':
                self.candidate_id.supporter_id.active = False
                self.candidate_id.active = False
            if self.departure_reason == 'demote':
                self.candidate_id.active = False
        else:
            raise UserError(_("Please Fill In The Given Informations"))

class ArchiveSupporter(models.TransientModel):
    _name="archive.supporter.wizard"
    _description="This model will handle the archiving of members"

    supporter_id = fields.Many2one('supporter.members')
    departure_reason = fields.Selection(selection=[('fired', 'Fired'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        if self.departure_reason and self.additional_information:
            archive = self.env['archived.information'].sudo().create({
                'supporter_id': self.supporter_id.id,
                'date_from': date.today(),
                'departure_reason': self.departure_reason,
                'additional_information': self.additional_information,
                'archived': True
            })
            self.supporter_id.active = False
        else:
            raise UserError(_("Please Fill In The Given Informations"))

class ArchiveDonor(models.TransientModel):
    _name="archive.donor.wizard"
    _description="This model will handle the archiving of members"


    donor_id = fields.Many2one('donors')
    departure_reason = fields.Selection(selection=[('fired', 'Fired'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        if self.departure_reason and self.additional_information:
            archive = self.env['archived.information'].sudo().create({
                'donor_id': self.donor_id.id,
                'date_from': date.today(),
                'departure_reason': self.departure_reason,
                'additional_information': self.additional_information,
                'archived': True
            })
            self.donor_id.active = False
        else:
            raise UserError(_("Please Fill In The Given Informations"))


# class CreateMember(models.TransientModel):
#     _name="create.member.wizard"
#     _description="This model will handle the creation of members"


#     def _default_years(self):
#         """This function will get the default years"""
#         years = []
#         eth_years = (datetime.now().year - 7)
#         for num in range(eth_years, 1979, -1):
#             years.append((str(num), num))
#         return years


#     wereda_id = fields.Many2one('membership.handlers.branch')
#     membership_org = fields.Many2one('membership.organization')
#     member_responsibility = fields.Many2one('members.responsibility', default=1, readonly=True)
#     main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", required=True)
#     cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]", required=True)
#     start_of_membership = fields.Selection(selection=_default_years, string='Membership Start Year')
#     stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', readonly=True)
#     national_id = fields.Char(translate=True)


#     def action_done(self):
#         """This function will be the action for wizards"""
#         partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
#         if self.national_id:
#             all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
#             if all_partner:
#                 raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
#             else:
#                 if self.membership_org and self.member_responsibility and self.start_of_membership:
#                     partner.write({
#                         'membership_org': self.membership_org.id,
#                         'member_responsibility': self.member_responsibility.id,
#                         'start_of_membership' :self.start_of_membership,
#                         'stock': self.stock,
#                         'national_id': self.national_id
#                     })
#                 else:
#                    raise UserError(_("Please Add All The Required Fields")) 
#         else:
#             raise UserError(_("Please Add A National ID"))


#     def action_cancel(self):
#         """This function will cancel archive"""
#         partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
#         partner.write({
#             'is_member': False,
#             'national_id': False
#         })   


class CreateLeader(models.TransientModel):
    _name="create.leader.wizard"
    _description="This model will handle the creation of leaders"


    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years


    registered_id = fields.Many2one('register.members')
    member_id = fields.Many2one('res.partner')
    leader_responsibility = fields.Many2one('leaders.responsibility')
    wereda_id = fields.Many2one('membership.handlers.branch')
    leader_sub_responsibility = fields.Many2many('leaders.sub.responsibility', domain="[('leaders_responsibility','in', [leader_responsibility])]", string="Leader's Sub Responsibility")
    national_id = fields.Char(translate=True, track_visibility='onchange')
    membership_org = fields.Many2one('membership.organization', track_visibility='onchange')
    main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]")
    member_ids = fields.Char(copy=False, readonly=True)
    leader_stock = fields.Selection(selection=[('appointed', 'Appointed'), ('not appointed', 'Not Appointed')], default='appointed', track_visibility='onchange', readonly=True)
    experience = fields.Char(translate=True, string="Experience Year")
    start_of_membership = fields.Selection(selection=_default_years, string='Membership Start Year')
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.leader.wizard'].search([('id', '=', self.id)])
        wizard.member_id.is_leader = True
        wizard.member_id.is_member = False
        wizard.member_id.demote_to_member = False
        wizard.member_id.demote = False


        if wizard.member_id.email_address and (wizard.member_id.email_address != wizard.member_id.user_name):
            user_exists = self.env['res.users'].sudo().search([('login', '=', wizard.member_id.user_name)])
            if user_exists:
                user_exists.unlink()
            existing = self.env['res.users'].sudo().search([('login', '=', wizard.member_id.email_address)])
            if existing:
                raise UserError(_("A User With Email Adress %s already exisits for %s. Please Make Sure Data isn't being Duplicated") % (wizard.member_id.email_address, wizard.member_id.name))
            else:
                wizard.member_id.user_name = wizard.member_id.email_address
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': wizard.member_id.email_address,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        if not wizard.member_id.user_name:
            name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-9:]
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
                
        if wizard.member_id.user_name and (('@' in wizard.member_id.user_name) and ('.' in wizard.member_id.user_name)) and not wizard.member_id.email_address:
            user_exists = self.env['res.users'].sudo().search([('login', '=', wizard.member_id.user_name)])
            if user_exists:
                user_exists.unlink()
            name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-9:]
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

        if not self.member_ids:
            code = self.env['ir.sequence'].next_by_code('res.partner')
            new = code[4:]
            ids = "AAPP/" + str(new) + "/" + str(wizard.member_id.subcity_id.unique_representation_code)  + "/" + str(wizard.member_id.wereda_id.unique_representation_code)
            self.member_ids = ids

        if self.leader_responsibility and self.national_id and self.membership_org and self.member_ids and self.leader_sub_responsibility and self.main_office_id and self.cell_id:
            wizard.member_id.write({
                'leader_responsibility': self.leader_responsibility.id,
                'leader_sub_responsibility': self.leader_sub_responsibility.ids,
                'leadership_status': self.leadership_status,
                'leader_stock': self.leader_stock,
                'national_id': self.national_id,
                'membership_org': self.membership_org.id,
                'member_ids': self.member_ids,
                'main_office': self.main_office_id.id,
                'member_cells': self.cell_id.id,
                'start_of_membership': self.start_of_membership
            })
            
            if self.leader_responsibility.id == 1:
                wizard.member_id.subcity_admin = False
                wizard.member_id.city_admin = False
            if self.leader_responsibility.id == 2:
                wizard.member_id.subcity_admin = True
                wizard.member_id.city_admin = False
            if self.leader_responsibility.id == 3:
                wizard.member_id.subcity_admin = False
                wizard.member_id.city_admin = True

        else:
            raise UserError(_("Please Add All The Given Fields")) 

        if not wizard.member_id.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    if not wizard.member_id.subcity_id.city_id.bypass_plannig:
                        plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved')])
                        city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_city:
                            if wizard.member_id.gender == 'Male':
                                plan_city.registered_male += 1
                                plan_city.total_registered += 1
                            if wizard.member_id.gender == 'Female':
                                plan_city.registered_female += 1
                                plan_city.total_registered += 1

                            for field in plan_city.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.member_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.member_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == wizard.member_id.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                            city_report.registered += 1
                            city_report.accomplished = (city_report.registered / plan_city.total_estimated) * 100
                            if plan_city.accomplished <= 50.00:
                                plan_city.colors = 'orange'
                            if 50 < plan_city.accomplished < 75:
                                plan_city.colors = 'blue'
                            if plan_city.accomplished >= 75:
                                plan_city.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved City Plan For Leader"))
                    if not wizard.member_id.subcity_id.bypass_plannig:
                        plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.member_id.subcity_id.id)])
                        subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_subcity:
                            if wizard.member_id.gender == 'Male':
                                plan_subcity.registered_male += 1
                                plan_subcity.total_registered += 1
                            if wizard.member_id.gender == 'Female':
                                plan_subcity.registered_female += 1
                                plan_subcity.total_registered += 1 

                            for field in plan_subcity.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.member_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.member_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == wizard.member_id.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                            subcity_report.registered += 1
                            subcity_report.accomplished = (subcity_report.registered / plan_subcity.total_estimated) * 100
                            if 30 <= plan_subcity.accomplished <= 50.00:
                                plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved')])
                                for plan in plan_subcities:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_subcity.colors = 'orange'
                            if 50 < plan_subcity.accomplished < 75:
                                plan_subcity.colors = 'blue'
                            if plan_subcity.accomplished >= 75:
                                plan_subcity.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Sub City Plan For Leader"))
                    if not wizard.member_id.wereda_id.bypass_plannig:
                        plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.member_id.wereda_id.id)])
                        wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_woreda:
                            if wizard.member_id.gender == 'Male':
                                plan_woreda.registered_male += 1
                                plan_woreda.total_registered += 1
                            if wizard.member_id.gender == 'Female':
                                plan_woreda.registered_female += 1
                                plan_woreda.total_registered += 1

                            for field in plan_woreda.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.member_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.member_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == wizard.member_id.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                            wereda_report.registered += 1
                            wereda_report.accomplished = (wereda_report.registered / plan_woreda.total_estimated) * 100                
                            if 30 <= plan_woreda.accomplished <= 50.00:
                                plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved')])
                                for plan in plan_woredas:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_woreda.colors = 'orange'
                            if 50 < plan_woreda.accomplished < 75:
                                plan_woreda.colors = 'blue'
                            if plan_woreda.accomplished >= 75:
                                plan_woreda.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Woreda Plan For Leader"))
            else:
                raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))
  
        wizard.member_id.member_cells.members_ids = [(3, int(wizard.member_id.id))]
        wizard.member_id.member_cells.leaders_ids = [(3, int(wizard.member_id.id))]

        all_members = self.cell_id.members_ids.ids + [wizard.member_id.id]
        all_members_mixed = self.cell_id.members_ids_mixed.ids + [wizard.member_id.id]

        self.cell_id.members_ids = [(5, 0, 0)]
        self.cell_id.members_ids_mixed = [(5, 0, 0)]

        self.cell_id.members_ids = [(6, 0, all_members)]
        self.cell_id.members_ids_mixed = [(6, 0, all_members_mixed)]


        mail_temp = self.env.ref('leader_approval')
        mail_temp.send_mail(wizard.member_id.id)
        wizard.registered_id.saved = True
        wizard.registered_id.unlink()
        user = self.env.user
        message = _("Congratulations!\n Leader has been Created.")
        title = _("<h4>Leader Created!</h4>")
        user.notify_success(message, title, True)          


class CreateLeague(models.TransientModel):
    _name="create.league.wizard"
    _description="This model will handle the creation of leagues"

    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 2000, -1):
            years.append((str(num), num))
        return years


    league_id = fields.Many2one('res.partner')
    registered_id = fields.Many2one('register.members')
    candidate_id = fields.Many2one('candidate.members')
    wereda_id = fields.Many2one('membership.handlers.branch')
    league_type = fields.Selection(selection=[('young', 'Youngster'), ('women', 'Woman')])
    membership_org = fields.Many2one('membership.organization', track_visibility='onchange', string="Organization")
    main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]")
    league_responsibility = fields.Many2one('league.responsibility', default=1, track_visibility='onchange', readonly=True)
    start_of_league = fields.Selection(selection=_default_years, string='League Start Year')


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.league.wizard'].search([('id', '=', self.id)])
        wizard.league_id.is_league = True
        wizard.league_id.was_league = True


        if wizard.league_id.email_address and (wizard.league_id.email_address != wizard.league_id.user_name):
            user_exists = self.env['res.users'].sudo().search([('login', '=', wizard.league_id.user_name)])
            if user_exists:
                user_exists.unlink()
            existing = self.env['res.users'].sudo().search([('login', '=', wizard.league_id.email_address)])
            if existing:
                raise UserError(_("A User With Email Adress %s already exisits for %s. Please Make Sure Data isn't being Duplicated") % (wizard.league_id.email_address, wizard.league_id.name))
            else:
                wizard.league_id.user_name = wizard.league_id.email_address
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': wizard.league_id.email_address,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

        if not wizard.league_id.has_user_name:
            name = wizard.league_id.name.split()[0] + wizard.league_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.league_id.name.split()[0] + wizard.league_id.phone[-9:]
                wizard.league_id.user_name = name
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.league_id.user_name = name
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

        if wizard.league_id.user_name and (('@' in wizard.league_id.user_name) and ('.' in wizard.league_id.user_name)) and not wizard.league_id.email_address:
            user_exists = self.env['res.users'].sudo().search([('login', '=', wizard.league_id.user_name)])
            if user_exists:
                user_exists.unlink()
            name = wizard.league_id.name.split()[0] + wizard.league_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.league_id.name.split()[0] + wizard.league_id.phone[-9:]
                wizard.league_id.user_name = name
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.league_id.user_name = name
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })



        if wizard.league_id.age >= 18:
            wizard.league_id.appropriate_age = True
        else:
            wizard.league_id.appropriate_age = False  

        if not wizard.league_id.member_ids:
            code = self.env['ir.sequence'].next_by_code('res.partner')
            new = code[4:]
            ids = "AAPP/" + str(new) + "/" + str(wizard.league_id.subcity_id.unique_representation_code) + "/" + str(wizard.league_id.wereda_id.unique_representation_code)
            wizard.league_id.member_ids = ids


        if self.membership_org and self.league_type and self.league_responsibility and self.start_of_league and self.main_office_id and self.cell_id:
            if wizard.league_id.gender == 'Male' and self.league_type == 'women':
                raise UserError(_("Only Women Can Join Woman League"))

            
            age_limit_young = self.env['age.range'].search([('for_which_stage', '=', 'young_league')])
            if not age_limit_young:
                raise UserError(_("Please Set Age Limit for Youngster League in the Configuration"))
            if self.league_type == 'young' and (wizard.league_id.age < age_limit_young.minimum_age_allowed or wizard.league_id.age > age_limit_young.maximum_age_allowed):
                raise UserError(_("This Age isn't within the Age Limit Range given for Youngster League"))

            age_limit_woman = self.env['age.range'].search([('for_which_stage', '=', 'woman_league')])
            if not age_limit_woman:
                raise UserError(_("Please Set Age Limit for Woman League in the Configuration"))
            if self.league_type == 'women' and (wizard.league_id.age < age_limit_woman.minimum_age_allowed or wizard.league_id.age > age_limit_woman.maximum_age_allowed):
                raise UserError(_("This Age isn't within the Age Limit Range given for Woman League"))

            wizard.league_id.write({
                'league_type': self.league_type,
                'league_organization': self.membership_org.id,
                'start_of_league': self.start_of_league,
                'league_responsibility': self.league_responsibility.id,
                # 'league_main_office': self.main_office_id.id,
                # 'league_member_cells': self.cell_id.id,
            })
            
        else:
            raise UserError(_("Please Add All The Given Fields"))

        if not wizard.league_id.subcity_id.city_id.bypass_plannig:  
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    if not wizard.league_id.subcity_id.city_id.bypass_plannig:
                        plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved')])
                        city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_city:
                            if wizard.league_id.gender == 'Male':
                                plan_city.registered_male += 1
                                plan_city.total_registered += 1
                            if wizard.league_id.gender == 'Female':
                                plan_city.registered_female += 1
                                plan_city.total_registered += 1

                            for field in plan_city.field_based_planning:
                                if field.field_for_league == 'education':
                                    if field.education_level.id == wizard.league_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_league == 'study field':
                                    if field.field_of_study_id.id == wizard.league_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100                           
                                if field.field_for_league == 'league type':
                                    if field.league_type == self.league_type:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 
                                if field.field_for_league == 'league org':
                                    if field.league_organization.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100


                            plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                            city_report.registered += 1
                            city_report.accomplished = (city_report.registered / plan_city.total_estimated) * 100
                            if plan_city.accomplished <= 50.00:
                                plan_city.colors = 'orange'
                            if 50 < plan_city.accomplished < 75:
                                plan_city.colors = 'blue'
                            if plan_city.accomplished >= 75:
                                plan_city.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved City Plan For League"))
                    if not wizard.league_id.subcity_id.bypass_plannig:
                        plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.league_id.subcity_id.id)])
                        subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_subcity and not wizard.league_id.subcity_id.bypass_plannig:
                            if wizard.league_id.gender == 'Male':
                                plan_subcity.registered_male += 1
                                plan_subcity.total_registered += 1
                            if wizard.league_id.gender == 'Female':
                                plan_subcity.registered_female += 1
                                plan_subcity.total_registered += 1 

                            for field in plan_subcity.field_based_planning:
                                if field.field_for_league == 'education':
                                    if field.education_level.id == wizard.league_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_league == 'study field':
                                    if field.field_of_study_id.id == wizard.league_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100                           
                                if field.field_for_league == 'league type':
                                    if field.league_type == self.league_type:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 
                                if field.field_for_league == 'league org':
                                    if field.league_organization.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100

                            plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                            subcity_report.registered += 1
                            subcity_report.accomplished = (subcity_report.registered / plan_subcity.total_estimated) * 100
                            if 30 <= plan_subcity.accomplished <= 50.00:
                                plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved')])
                                for plan in plan_subcities:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_subcity.colors = 'orange'
                            if 50 < plan_subcity.accomplished < 75:
                                plan_subcity.colors = 'blue'
                            if plan_subcity.accomplished >= 75:
                                plan_subcity.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Sub City Plan For League"))
                    if  not wizard.league_id.wereda_id.bypass_plannig:
                        plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.league_id.wereda_id.id)])
                        wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_woreda:
                            if wizard.league_id.gender == 'Male':
                                plan_woreda.registered_male += 1
                                plan_woreda.total_registered += 1
                            if wizard.league_id.gender == 'Female':
                                plan_woreda.registered_female += 1
                                plan_woreda.total_registered += 1

                            for field in plan_woreda.field_based_planning:
                                if field.field_for_league == 'education':
                                    if field.education_level.id == wizard.league_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_league == 'study field':
                                    if field.field_of_study_id.id == wizard.league_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100                           
                                if field.field_for_league == 'league type':
                                    if field.league_type == self.league_type:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 
                                if field.field_for_league == 'league org':
                                    if field.league_organization.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100

                            plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                            wereda_report.registered += 1
                            wereda_report.accomplished = (wereda_report.registered / plan_woreda.total_estimated) * 100
                            if 30 <= plan_woreda.accomplished <= 50.00:
                                plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved')])
                                for plan in plan_woredas:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_woreda.colors = 'orange'
                            if 50 < plan_woreda.accomplished < 75:
                                plan_woreda.colors = 'blue'
                            if plan_woreda.accomplished >= 75:
                                plan_woreda.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Woreda Plan For League"))
            else:
                raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))

        wizard.candidate_id.state = 'approved'
        wizard.candidate_id.partner_id = wizard.league_id.id 

        # ADDING MEMBER INTO CELL
        wizard.candidate_id.cell_id.candidate_ids = [(3, int(wizard.candidate_id.id))]
        all_members = self.cell_id.leagues_ids.ids + [wizard.league_id.id]
        all_members_mixed = self.cell_id.leagues_ids_mixed.ids + [wizard.league_id.id]

        self.cell_id.leagues_ids = [(5, 0, 0)]
        self.cell_id.leagues_ids_mixed = [(5, 0, 0)]

        self.cell_id.leagues_ids = [(6, 0, all_members)]
        self.cell_id.leagues_ids_mixed = [(6, 0, all_members_mixed)]

        mail_temp = self.env.ref('league_approval')
        mail_temp.send_mail(wizard.league_id.id)
        user = self.env.user
        message = _("Congratulations!\n League has been Created.")
        title =_("<h4>League Created!</h4>")
        user.notify_success(message, title, True) 


# class CreateAttachment(models.TransientModel):
#     _name="attachment.wizard"
#     _description="This model will handle the archiving of members"

#     name = fields.Char(translate=True)
#     res_model = fields.Char()
#     res_id = fields.Many2oneReference('Resource ID', model_field='res_model')
#     member_id = fields.Many2one('res.partner')
#     attachment_type = fields.Many2one('attachment.type')
#     description = fields.Text('Description')
#     type = fields.Selection([('url', 'URL'), ('binary', 'File')])
#     datas = fields.Binary()


#     def action_done(self):
#         """This function will be the action for wizards"""
#         wizard = self.env['attachment.wizard'].search([('id', '=', self.id)])
#         if self.name and self.attachment_type and self.datas:
#             attachment = self.env['ir.attachment'].sudo().create({
#                 'name': self.name,
#                 'res_model': wizard.res_model,
#                 'res_id': wizard.res_id,
#                 'attachment_type': self.attachment_type.id,
#                 'description': self.description,
#                 'type': 'binary',
#                 'datas': self.datas
#             })
#             user = self.env.user
#             message = _("Appointment has been successfully uploaded.")
#             title =_("<h4>Uploaded!</h4>")
#             user.notify_success(message, title, True)  
                              
#         else:
#             raise UserError(_("Please Add All The Given Fields"))


class CreateLeagueMember(models.TransientModel):
    _name="create.from.league.wizard"
    _description="This model will handle the creation of members"

    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years

    member_id = fields.Many2one('res.partner')
    wereda_id = fields.Many2one('membership.handlers.branch')
    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility', default=1, readonly=True)
    main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]")
    start_of_membership = fields.Selection(selection=_default_years, string='Membership Start Year')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', readonly=True)
    national_id = fields.Char(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.from.league.wizard'].search([('id', '=', self.id)])
        wizard.member_id.is_member = True
        wizard.member_id.was_member = True

        # if wizard.member_id.income == 0.00:
        #     wizard.member_id.payment_method = 'cash'
        #     wizard.member_id.membership_monthly_fee_cash = 0.00
        # else:
        #     all_fee = self.env['payment.fee.configuration'].search([])
        #     for fee in all_fee:
        #         if fee.minimum_wage <= wizard.member_id.income <= fee.maximum_wage:
        #             wizard.member_id.payment_method = 'percentage'
        #             wizard.member_id.membership_monthly_fee_percent = fee.fee_in_percent
        #             wizard.member_id.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * wizard.member_id.income
        #             break
        #         else:
        #             wizard.member_id.payment_method = 'percentage'
        #             wizard.member_id.membership_monthly_fee_percent = fee.fee_in_percent
        #             wizard.member_id.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * wizard.member_id.income
        #             continue


        if wizard.member_id.email_address and (wizard.member_id.email_address != wizard.member_id.user_name):
            user_exists = self.env['res.users'].sudo().search([('login', '=', wizard.member_id.user_name)])
            if user_exists:
                user_exists.unlink()
            existing = self.env['res.users'].sudo().search([('login', '=', wizard.member_id.email_address)])
            if existing:
                raise UserError(_("A User With Email Adress %s already exisits for %s. Please Make Sure Data isn't being Duplicated") % (wizard.member_id.email_address, wizard.member_id.name))
            else:
                wizard.member_id.user_name = wizard.member_id.email_address
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': wizard.member_id.email_address,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        if not wizard.member_id.user_name:
            name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-9:]
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

        if wizard.member_id.user_name and (('@' in wizard.member_id.user_name) and ('.' in wizard.member_id.user_name)) and not wizard.member_id.email_address:
            user_exists = self.env['res.users'].sudo().search([('login', '=', wizard.member_id.user_name)])
            if user_exists:
                user_exists.unlink()
            name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-9:]
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

                
        if not wizard.member_id.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    if not wizard.member_id.subcity_id.city_id.bypass_plannig:
                        plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                        city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                        if plan_city:
                            if wizard.member_id.gender == 'Male':
                                plan_city.registered_male += 1
                                plan_city.total_registered += 1
                            if wizard.member_id.gender == 'Female':
                                plan_city.registered_female += 1
                                plan_city.total_registered += 1

                            for field in plan_city.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.member_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.member_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                            city_report.registered += 1
                            city_report.accomplished = (city_report.registered / plan_city.total_estimated) * 100
                            if plan_city.accomplished <= 50.00:
                                plan_city.colors = 'orange'
                            if 50 < plan_city.accomplished < 75:
                                plan_city.colors = 'blue'
                            if plan_city.accomplished >= 75:
                                plan_city.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved City Plan For Member"))
                    if not wizard.member_id.subcity_id.bypass_plannig:
                        plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.member_id.subcity_id.id)])
                        subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_subcity:
                            if wizard.member_id.gender == 'Male':
                                plan_subcity.registered_male += 1
                                plan_subcity.total_registered += 1
                            if wizard.member_id.gender == 'Female':
                                plan_subcity.registered_female += 1
                                plan_subcity.total_registered += 1 


                            for field in plan_subcity.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.member_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.member_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                            subcity_report.registered += 1
                            subcity_report.accomplished = (subcity_report.registered / plan_subcity.total_estimated) * 100
                            if 30 <= plan_subcity.accomplished <= 50.00:
                                plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                                for plan in plan_subcities:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_subcity.colors = 'orange'
                            if 50 < plan_subcity.accomplished < 75:
                                plan_subcity.colors = 'blue'
                            if plan_subcity.accomplished >= 75:
                                plan_subcity.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Sub City Plan For Member"))
                    if not wizard.member_id.wereda_id.bypass_plannig:
                        plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.member_id.wereda_id.id)])
                        wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_woreda:
                            if wizard.member_id.gender == 'Male':
                                plan_woreda.registered_male += 1
                                plan_woreda.total_registered += 1
                            if wizard.member_id.gender == 'Female':
                                plan_woreda.registered_female += 1
                                plan_woreda.total_registered += 1


                            for field in plan_woreda.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.member_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.member_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                            wereda_report.registered += 1
                            wereda_report.accomplished = (wereda_report.registered / plan_woreda.total_estimated) * 100
                            if 30 <= plan_woreda.accomplished <= 50.00:
                                plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                                for plan in plan_woredas:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_woreda.colors = 'orange'
                            if 50 < plan_woreda.accomplished < 75:
                                plan_woreda.colors = 'blue'
                            if plan_woreda.accomplished >= 75:
                                plan_woreda.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Woreda Plan For Member"))
            else:
                raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))

        if self.national_id:
            all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
            if all_partner:
                raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
            else:
                if self.membership_org and self.member_responsibility and self.start_of_membership and self.main_office_id and self.cell_id:
                    wizard.member_id.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership': self.start_of_membership,
                        'stock': self.stock,
                        'national_id': self.national_id,
                        'main_office': self.main_office_id.id,
                        'member_cells': self.cell_id.id,
                    })
                else:
                    raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))

        all_members = self.cell_id.members_ids.ids + [wizard.member_id.id]
        all_members_mixed = self.cell_id.members_ids_mixed.ids + [wizard.member_id.id]

        self.cell_id.members_ids = [(5, 0, 0)]
        self.cell_id.members_ids_mixed = [(5, 0, 0)]

        self.cell_id.members_ids = [(6, 0, all_members)]
        self.cell_id.members_ids_mixed = [(6, 0, all_members_mixed)]


        mail_temp = self.env.ref('member_approval')
        mail_temp.send_mail(wizard.member_id.id)
        user = self.env.user
        message = _("Congratulations!\n Member has been Created.")
        title = _("<h4>Member Created!</h4>")
        user.notify_success(message, title, True)  



class CreateCandidateMember(models.TransientModel):
    _name="create.from.candidate.wizard"
    _description="This model will handle the creation of members"


    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years



    candidate_id = fields.Many2one('candidate.members')
    wereda_id = fields.Many2one('membership.handlers.branch')
    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility', default=1, readonly=True)
    main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", required=True)
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]", required=True)
    start_of_membership = fields.Selection(selection=_default_years, string='Membership Start Year')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', readonly=True)
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.from.candidate.wizard'].search([('id', '=', self.id)])
        code = self.env['ir.sequence'].next_by_code('res.partner')
        new = code[4:]
        ids = "AAPP/" + str(new) + "/" + str(wizard.candidate_id.subcity_id.unique_representation_code) + "/" + str(wizard.candidate_id.wereda_id.unique_representation_code)
        partner = self.env['res.partner'].create({
            'image_1920': wizard.candidate_id.image_1920,
            'name': wizard.candidate_id.name,
            'first_name': wizard.candidate_id.first_name,
            'father_name': wizard.candidate_id.father_name,
            'grand_father_name': wizard.candidate_id.grand_father_name,
            'gender': wizard.candidate_id.gender,
            'age': wizard.candidate_id.age,
            'date': wizard.candidate_id.date,
            'ethnic_group': wizard.candidate_id.ethnic_group.id,
            'education_level': wizard.candidate_id.education_level.id,
            'field_of_study_id': wizard.candidate_id.field_of_study_id.id,
            'income': wizard.candidate_id.income,
            'subcity_id': wizard.candidate_id.subcity_id.id,
            'wereda_id': wizard.candidate_id.wereda_id.id,
            'residential_subcity_id': wizard.candidate_id.residential_subcity_id.id,
            'residential_wereda_id': wizard.candidate_id.residential_wereda_id.id,
            'phone': wizard.candidate_id.phone,
            'house_number': wizard.candidate_id.house_number,
            'email_address': wizard.candidate_id.email_address,
            'is_user_input': wizard.candidate_id.is_user_input,
            'user_input': wizard.candidate_id.user_input,
            'was_candidate': True,
            'was_supporter': True,
            'was_member': True,
            'is_member': True,
            'is_leader': False,
            'is_league': False,
            'candidate_id': wizard.candidate_id.id,
            'supporter_id': wizard.candidate_id.supporter_id.id,
            'member_ids': ids

        })

        for ed in wizard.candidate_id.educational_history:
            partner.write({
                'educational_history': [(0, 0, {
                    'education_level': ed.education_level.id,
                    'field_of_study_id': ed.field_of_study_id.id
                })],
            })
        for experience in wizard.candidate_id.work_experience_ids:
            partner.write({
                'work_experience_ids': [(0, 0, {
                    'name': experience.name,
                    'place_of_work': experience.place_of_work,
                    'years_of_service': experience.years_of_service,
                    'current_job': experience.current_job
                })],
            })
        if wizard.candidate_id.income == 0.00:
            partner.write({
                'payment_method': 'cash',
                'membership_monthly_fee_percent': 0.00,
                'membership_monthly_fee_cash': 0.00
            })
        else:
            all_fee = self.env['payment.fee.configuration'].search([])
            for fee in all_fee:
                if fee.minimum_wage <= wizard.candidate_id.income <= fee.maximum_wage:
                    partner.write({
                        'payment_method': 'percentage',
                        'membership_monthly_fee_percent': fee.fee_in_percent,
                        'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * wizard.candidate_id.income,
                    })
                    break
                else:
                    partner.write({
                        'payment_method': 'percentage',
                        'membership_monthly_fee_percent': fee.fee_in_percent,
                        'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * wizard.candidate_id.income,
                    })
                    continue

        if partner.email_address:
            existing = self.env['res.users'].sudo().search([('login', '=', partner.email_address)])
            if existing:
                raise UserError(_("A User With Email Adress %s already exisits for %s. Please Make Sure Data isn't being Duplicated") % (partner.email_address, partner.name))
            else:
                partner.user_name = partner.email_address
                partner.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': partner.email_address,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        else:
            name = partner.name.split()[0] + partner.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = partner.name.split()[0] + partner.phone[-9:]
                partner.user_name = name
                partner.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                partner.user_name = name
                partner.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '12345678',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

        wizard.candidate_id.state = 'approved'
        wizard.candidate_id.partner_id = partner.id

        if not wizard.candidate_id.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    if not wizard.candidate_id.subcity_id.city_id.bypass_plannig:
                        plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                        city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_city:
                            if wizard.candidate_id.gender == 'Male':
                                plan_city.registered_male += 1
                                plan_city.total_registered += 1
                            if wizard.candidate_id.gender == 'Female':
                                plan_city.registered_female += 1
                                plan_city.total_registered += 1

                            for field in plan_city.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.candidate_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.candidate_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100   

                            plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                            city_report.registered += 1
                            city_report.accomplished = (city_report.registered / plan_city.total_estimated) * 100
                            if plan_city.accomplished <= 50.00:
                                plan_city.colors = 'orange'
                            if 50 < plan_city.accomplished < 75:
                                plan_city.colors = 'blue'
                            if plan_city.accomplished >= 75:
                                plan_city.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved City Plan For Member"))
                    if not wizard.candidate_id.subcity_id.bypass_plannig:
                        plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.candidate_id.subcity_id.id)])
                        subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_subcity:
                            if wizard.candidate_id.gender == 'Male':
                                plan_subcity.registered_male += 1
                                plan_subcity.total_registered += 1
                            if wizard.candidate_id.gender == 'Female':
                                plan_subcity.registered_female += 1
                                plan_subcity.total_registered += 1 

                            for field in plan_subcity.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.candidate_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.candidate_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                            subcity_report.registered += 1
                            subcity_report.accomplished = (subcity_report.registered / plan_subcity.total_estimated) * 100
                            if 30 <= plan_subcity.accomplished <= 50.00:
                                plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                                for plan in plan_subcities:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_subcity.colors = 'orange'
                            if 50 < plan_subcity.accomplished < 75:
                                plan_subcity.colors = 'blue'
                            if plan_subcity.accomplished >= 75:
                                plan_subcity.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Sub City Plan For Member"))
                    if not wizard.candidate_id.wereda_id.bypass_plannig:
                        plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.candidate_id.wereda_id.id)])
                        wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_woreda:
                            if wizard.candidate_id.gender == 'Male':
                                plan_woreda.registered_male += 1
                                plan_woreda.total_registered += 1
                            if wizard.candidate_id.gender == 'Female':
                                plan_woreda.registered_female += 1
                                plan_woreda.total_registered += 1

                            for field in plan_woreda.field_based_planning:
                                if field.field_for_member == 'education':
                                    if field.education_level.id == wizard.candidate_id.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'study field':
                                    if field.field_of_study_id.id == wizard.candidate_id.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_member == 'membership organization':
                                    if field.membership_org.id == self.membership_org.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100 

                            plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                            wereda_report.registered += 1
                            wereda_report.accomplished = (wereda_report.registered / plan_woreda.total_estimated) * 100
                            if 30 <= plan_woreda.accomplished <= 50.00:
                                plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                                for plan in plan_woredas:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_woreda.colors = 'orange'
                            if 50 < plan_woreda.accomplished < 75:
                                plan_woreda.colors = 'blue'
                            if plan_woreda.accomplished >= 75:
                                plan_woreda.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Woreda Plan For Member"))
            else:
                raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))

        if self.national_id:
            all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
            if all_partner:
                raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
            else:
                if self.membership_org and self.member_responsibility and self.start_of_membership and self.main_office_id and self.cell_id:
                    partner.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership': self.start_of_membership,
                        # 'main_office': self.main_office_id.id,
                        # 'member_cells': self.cell_id.id,
                        'stock': self.stock,
                        'national_id': self.national_id,
                    })
                else:
                    raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))


        # ADDING MEMBER INTO CELL
        wizard.candidate_id.cell_id.candidate_ids = [(3, int(wizard.candidate_id.id))]
        all_members = self.cell_id.members_ids.ids + [partner.id]
        all_members_mixed = self.cell_id.members_ids_mixed.ids + [partner.id]

        self.cell_id.members_ids = [(5, 0, 0)]
        self.cell_id.members_ids_mixed = [(5, 0, 0)]

        self.cell_id.members_ids = [(6, 0, all_members)]
        self.cell_id.members_ids_mixed = [(6, 0, all_members_mixed)]

        mail_temp = self.env.ref('candidate_approval')
        mail_temp.send_mail(wizard.candidate_id.id)
        wizard.candidate_id.deactivate_activity(wizard.candidate_id)
        user = self.env.user
        message = _("Congratulations!\n Member has been Created.")
        title =_("<h4>Member Created!</h4>")
        user.notify_success(message, title, True)  
