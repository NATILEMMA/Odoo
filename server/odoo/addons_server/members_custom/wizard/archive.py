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
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    cells = fields.Many2one('member.cells', domain="['|', ('main_office', '=', main_office), ('main_office_league', '=', main_office)]")


    @api.onchange('main_office')
    def _check_admins(self):
        """This function will check if a cell has a main office administrator"""
        if self.main_office:
            if not self.main_office.main_admin:
                raise UserError(_("The Selected Main Office Doesn't Have A Main Office Administrator"))        

    @api.onchange('cells')
    def _remove_main_office(self):
        """This function will check to make sure main office comes first"""
        if self.cells and not self.main_office:
            self.cells = False
            self.main_office = False
        if self.cells and self.main_office:
            if not self.cells.cell_admin:
                raise UserError(_("The Selected Cell Doesn't Have A Cell Administrator"))

    def action_done(self):
        """This function will be the action for wizards"""
        if self.main_office and self.cells:
            wizard = self.env['send.supporters'].search([('id', '=', self.id)])
            user = self.env.user
            if wizard.supporter_id:
                message = str(wizard.supporter_id.name) + "'s 3 month has Passed. Please Make A Decision About The State of Their Candidacy."
                model = self.env['ir.model'].search([('model', '=', 'supporter.members'), ('is_mail_activity', '=', True)])
                activity_type = self.env['mail.activity.type'].search([('name', '=', 'Supporter Approval')], limit=1)

                if self.main_office.main_admin:
                    activity = self.env['mail.activity'].create({
                        'display_name': message,
                        'summary': "Supporter Approval",
                        'date_deadline': date.today() + relativedelta(month=2),
                        'user_id': self.main_office.main_admin.id,
                        'res_model_id': model.id,
                        'res_id': wizard.supporter_id.id,
                        'activity_type_id': activity_type.id
                    })
                    self.main_office.main_admin.notify_warning(message, '<h4>Supporter Approval</h4>', True)

                if self.cells.cell_admin:
                    activity = self.env['mail.activity'].create({
                        'display_name': message,
                        'summary': "Supporter Approval",
                        'date_deadline': date.today() + relativedelta(month=2),
                        'user_id': self.cells.cell_admin.id,
                        'res_model_id': model.id,
                        'res_id': wizard.supporter_id.id,
                        'activity_type_id': activity_type.id                
                    })
                    self.cells.cell_admin.notify_warning(message, '<h4>Supporter Approval</h4>', True)

                # wizard.supporter_id.deactivate_activity(wizard.supporter_id)
            if wizard.candidate_id:
                message = str(wizard.candidate_id.name) + "'s 6 month has Passed. Please Make A Decision About The State of Their Candidacy."
                model = self.env['ir.model'].search([('model', '=', 'candidate.members'), ('is_mail_activity', '=', True)])
                activity_type = self.env['mail.activity.type'].search([('name', '=', 'Candidate Approval')], limit=1)

                if self.main_office.main_admin:
                    activity = self.env['mail.activity'].create({
                        'display_name': message,
                        'summary': "Candidate Approval",
                        'date_deadline': date.today() + relativedelta(month=2),
                        'user_id': self.main_office.main_admin.id,
                        'res_model_id': model.id,
                        'res_id': wizard.candidate_id.id,
                        'activity_type_id': activity_type.id
                    })
                    print(activity.user_id)
                    self.main_office.main_admin.notify_warning(message, '<h4>Supporter Approval</h4>', True)

                if self.cells.cell_admin:
                    activity = self.env['mail.activity'].create({
                        'display_name': message,
                        'summary': "Candidate Approval",
                        'date_deadline': date.today() + relativedelta(month=2),
                        'user_id': self.cells.cell_admin.id,
                        'res_model_id': model.id,
                        'res_id': wizard.candidate_id.id,
                        'activity_type_id': activity_type.id                
                    })
                    self.cells.cell_admin.notify_warning(message, '<h4>Candidate Approval</h4>', True)

                # wizard.candidate_id.deactivate_activity(wizard.candidate_id)
            user.notify_success("Approval Has Been Sent", '<h4>Approval Sent</h4>', True)
        else:
            raise UserError(_("Please Fill In The Given Informations"))

class ArchiveMembers(models.TransientModel):
    _name="archive.members.wizard"
    _description="This model will handle the archiving members"

    member_id = fields.Many2one('res.partner')
    is_leader = fields.Boolean(related="member_id.is_leader")
    is_member = fields.Boolean(related="member_id.is_member")
    is_league = fields.Boolean(related="member_id.is_league")
    demote_to_for_leader = fields.Selection(selection=[('member', 'Member'), ('candidate', 'Candidate'), ('supporter', 'Supporter')], default='member')
    demote_to_for_member = fields.Selection(selection=[('league', 'League'), ('candidate', 'Candidate'), ('supporter', 'Supporter')], default='candidate')
    departure_reason = fields.Selection(selection=[('fired', 'Fired'),  ('demote', 'Demote'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    departure_reason_league = fields.Selection(selection=[('fired', 'Fired'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)


    def action_done(self):
        """This function will be the action for wizards"""
        if self.departure_reason and self.additional_information:
            archive = self.env['archived.information'].sudo().create({
                'member_id': self.member_id.id,
                'date_from': date.today(),
                'departure_reason': self.departure_reason,
                'additional_information': self.additional_information,
                'archived': True
            })
            if self.departure_reason_league == 'resigned' or self.departure_reason_league == 'retired' or self.departure_reason_league == 'death' or self.departure_reason_league == 'fired':
                user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                user.write({
                    'active': False
                })
                self.member_id.active = False
            if self.departure_reason == 'resigned' or self.departure_reason == 'retired' or self.departure_reason == 'death' or self.departure_reason == 'fired':
                user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                user.write({
                    'active': False
                })
                self.member_id.candidate_id.active = False
                self.member_id.supporter_id.active = False
                self.member_id.active = False
            if self.departure_reason == 'demote' and self.is_leader == True:
                if self.demote_to_for_leader == 'member':
                    self.member_id.is_leader = False
                    self.member_id.is_member = True
                    self.member_id.demote = True
                if self.demote_to_for_leader == 'candidate':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.active = False
                if self.demote_to_for_leader == 'supporter':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.candidate_id.active = False
                    self.member_id.active = False
                if self.demote_to_for_member == 'league':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.is_leader = False
            if self.departure_reason == 'demote' and self.is_member == True:
                if self.demote_to_for_member == 'candidate':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.active = False
                if self.demote_to_for_member == 'supporter':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.candidate_id.active = False
                    self.member_id.active = False
                if self.demote_to_for_member == 'league':
                    if self.member_id.user_name:
                        user = self.env['res.users'].search([('partner_id', '=', self.member_id.id)])
                        user.write({
                            'active': False
                        })
                    self.member_id.is_member = False
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


class CreateMember(models.TransientModel):
    _name="create.member.wizard"
    _description="This model will handle the creation of members"

    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility', default=1, readonly=True)
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', readonly=True)
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if self.national_id:
            all_partner = self.env['res.partner'].search([('national_id', '=', self.national_id)])
            if all_partner:
                raise UserError(_("A Member With This National Id Already Exists. You might be duplicating a record."))
            else:
                if self.membership_org and self.member_responsibility and self.start_of_membership:
                    partner.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership' :self.start_of_membership,
                        'stock': self.stock,
                        'national_id': self.national_id
                    })
                else:
                   raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))


    def action_cancel(self):
        """This function will cancel archive"""
        partner = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        partner.write({
            'is_member': False,
            'national_id': False
        })   


class CreateLeader(models.TransientModel):
    _name="create.leader.wizard"
    _description="This model will handle the creation of leaders"

    registered_id = fields.Many2one('register.members')
    member_id = fields.Many2one('res.partner')
    leader_responsibility = fields.Many2one('leaders.responsibility')
    national_id = fields.Char(translate=True, track_visibility='onchange')
    membership_org = fields.Many2one('membership.organization', track_visibility='onchange')
    member_ids = fields.Char(copy=False, readonly=True)
    leader_stock = fields.Selection(selection=[('appointed', 'Appointed'), ('not appointed', 'Not Appointed')], default='appointed', track_visibility='onchange', readonly=True)
    experience = fields.Char(translate=True, string="Experience Year")
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.leader.wizard'].search([('id', '=', self.id)])
        wizard.member_id.is_leader = True
        wizard.member_id.is_member = False
        wizard.member_id.demote_to_member = False
        wizard.member_id.demote = False
        if wizard.member_id.phone and not wizard.member_id.user_name:
            name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-9:]
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        if not wizard.member_id.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved')])
                    city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                    if plan_city and not wizard.member_id.subcity_id.city_id.bypass_plannig:
                        if wizard.member_id.gender == 'Male':
                            plan_city.registered_male += 1
                            plan_city.total_registered += 1
                        if wizard.member_id.gender == 'Female':
                            plan_city.registered_female += 1
                            plan_city.total_registered += 1

                        for field in plan_city.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.member_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                    plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.member_id.subcity_id.id)])
                    subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                    if plan_subcity and not wizard.member_id.subcity_id.bypass_plannig:
                        if wizard.member_id.gender == 'Male':
                            plan_subcity.registered_male += 1
                            plan_subcity.total_registered += 1
                        if wizard.member_id.gender == 'Female':
                            plan_subcity.registered_female += 1
                            plan_subcity.total_registered += 1 

                        for field in plan_subcity.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.member_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                    plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'leader'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.member_id.wereda_id.id)])
                    wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                    if plan_woreda and not wizard.member_id.wereda_id.bypass_plannig:
                        if wizard.member_id.gender == 'Male':
                            plan_woreda.registered_male += 1
                            plan_woreda.total_registered += 1
                        if wizard.member_id.gender == 'Female':
                            plan_woreda.registered_female += 1
                            plan_woreda.total_registered += 1

                        for field in plan_woreda.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.member_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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

        if not self.member_ids:
            code = self.env['ir.sequence'].next_by_code('res.partner')
            new = code[4:]
            ids = "AAPP/" + str(new) + "/" + str(wizard.member_id.subcity_id.name)
            self.member_ids = ids

        if self.leader_responsibility and self.experience and self.leader_stock and self.national_id and self.membership_org and self.member_ids:
            wizard.member_id.write({
                'leader_responsibility': self.leader_responsibility.id,
                'experience': self.experience,
                'leadership_status': self.leadership_status,
                'leader_stock': self.leader_stock,
                'national_id': self.national_id,
                'membership_org': self.membership_org.id,
                'member_ids': self.member_ids,
                'start_of_membership': self.start_of_membership
            })
            wizard.registered_id.saved = True
            wizard.registered_id.unlink()
            user = self.env.user
            user.notify_success("Congratulations!\n Leader has been Created.", '<h4>Leader Created!</h4>', True)  
        else:
            raise UserError(_("Please Add All The Given Fields"))            

        mail_temp = self.env.ref('members_custom.leader_approval')
        mail_temp.send_mail(wizard.member_id.id)


class CreateLeague(models.TransientModel):
    _name="create.league.wizard"
    _description="This model will handle the creation of leagues"

    league_id = fields.Many2one('res.partner')
    registered_id = fields.Many2one('register.members')
    league_type = fields.Selection(selection=[('young', 'Youngsters'), ('women', 'Women')])
    league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')])
    league_responsibility = fields.Many2one('league.responsibility', default=1, track_visibility='onchange', readonly=True)
    start_of_league = fields.Selection(selection=[(str(num), num) for num in range(2001, (datetime.now().year)+1 )], string='League Start Year')


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.league.wizard'].search([('id', '=', self.id)])
        wizard.league_id.is_league = True
        wizard.league_id.was_league = True
        if wizard.league_id.phone and not wizard.league_id.user_name:
            name = wizard.league_id.name.split()[0] + wizard.league_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.league_id.name.split()[0] + wizard.league_id.phone[-9:]
                wizard.league_id.user_name = name
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.league_id.user_name = name
                wizard.league_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.league_id.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        if wizard.league_id.age >= 18:
            wizard.league_id.appropriate_age = True
        else:
            wizard.league_id.appropriate_age = False  

        if not wizard.league_id.member_ids:
            code = self.env['ir.sequence'].next_by_code('res.partner')
            new = code[4:]
            ids = "AAPP/" + str(new) + "/" + str(wizard.league_id.subcity_id.name)
            wizard.league_id.member_ids = ids


        if self.league_org and self.league_type and self.league_responsibility and self.start_of_league:
            if wizard.league_id.gender == 'Male' and self.league_type == 'women':
                raise UserError(_("Only Women Can Join Women League")) 
            wizard.league_id.write({
                'league_type': self.league_type,
                'league_org': self.league_org,
                'start_of_league': self.start_of_league,
                'league_responsibility': self.league_responsibility.id
            })
            wizard.registered_id.saved = True
            wizard.registered_id.unlink()
            user = self.env.user
            user.notify_success("Congratulations!\n League has been Created.", '<h4>League Created!</h4>', True)  
        else:
            raise UserError(_("Please Add All The Given Fields"))

        if not wizard.league_id.subcity_id.city_id.bypass_plannig:  
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved')])
                    city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_city and not wizard.league_id.subcity_id.city_id.bypass_plannig:
                        if wizard.league_id.gender == 'Male':
                            plan_city.registered_male += 1
                            plan_city.total_registered += 1
                        if wizard.league_id.gender == 'Female':
                            plan_city.registered_female += 1
                            plan_city.total_registered += 1

                        for field in plan_city.field_based_planning:
                            if field.field_for_league == 'ethnic':
                                if field.ethnic_group.id == wizard.league_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                                if field.league_org == self.league_org:
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
                            if field.field_for_league == 'ethnic':
                                if field.ethnic_group.id == wizard.league_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                                if field.league_org == self.league_org:
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
                    plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'league'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.league_id.wereda_id.id)])
                    wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_woreda and not wizard.league_id.wereda_id.bypass_plannig:
                        if wizard.league_id.gender == 'Male':
                            plan_woreda.registered_male += 1
                            plan_woreda.total_registered += 1
                        if wizard.league_id.gender == 'Female':
                            plan_woreda.registered_female += 1
                            plan_woreda.total_registered += 1

                        for field in plan_woreda.field_based_planning:
                            if field.field_for_league == 'ethnic':
                                if field.ethnic_group.id == wizard.league_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                                if field.league_org == self.league_org:
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


        mail_temp = self.env.ref('members_custom.league_approval')
        mail_temp.send_mail(wizard.league_id.id)

class CreateAttachment(models.TransientModel):
    _name="attachment.wizard"
    _description="This model will handle the archiving of members"

    name = fields.Char(translate=True)
    res_model = fields.Char()
    res_id = fields.Many2oneReference('Resource ID', model_field='res_model')
    attachment_type = fields.Many2one('attachment.type')
    description = fields.Text('Description')
    type = fields.Selection([('url', 'URL'), ('binary', 'File')])
    datas = fields.Binary()


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['attachment.wizard'].search([('id', '=', self.id)])
        if self.name and self.attachment_type and self.datas:
            attachment = self.env['ir.attachment'].sudo().create({
                'name': self.name,
                'res_model': wizard.res_model,
                'res_id': wizard.res_id,
                'attachment_type': self.attachment_type.id,
                'description': self.description,
                'type': 'binary',
                'datas': self.datas
            })
        else:
            raise UserError(_("Please Add All The Given Fields"))


class CreateLeagueMember(models.TransientModel):
    _name="create.from.league.wizard"
    _description="This model will handle the creation of members"

    member_id = fields.Many2one('res.partner')
    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility', default=1, readonly=True)
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', readonly=True)
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.from.league.wizard'].search([('id', '=', self.id)])
        code = self.env['ir.sequence'].next_by_code('res.partner')
        new = code[4:]
        wizard.member_id.member_ids = "AAPP/" + str(new) + "/" + str(wizard.member_id.subcity_id.name)
        wizard.member_id.is_member = True
        wizard.member_id.was_member = True

        if wizard.member_id.income == 0.00:
            wizard.member_id.payment_method = 'cash'
            wizard.member_id.membership_monthly_fee_cash = 0.00
        else:
            all_fee = self.env['payment.fee.configuration'].search([])
            for fee in all_fee:
                if fee.minimum_wage <= wizard.member_id.income <= fee.maximum_wage:
                    wizard.member_id.payment_method = 'percentage'
                    wizard.member_id.membership_monthly_fee_percent = fee.fee_in_percent
                    wizard.member_id.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * wizard.member_id.income
                    break
                else:
                    wizard.member_id.payment_method = 'percentage'
                    wizard.member_id.membership_monthly_fee_percent = fee.fee_in_percent
                    wizard.member_id.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * wizard.member_id.income
                    continue

        if wizard.member_id.phone and not wizard.member_id.user_name:
            name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = wizard.member_id.name.split()[0] + wizard.member_id.phone[-9:]
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                wizard.member_id.user_name = name
                wizard.member_id.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': wizard.member_id.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        if not wizard.member_id.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                    city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                    if plan_city and not wizard.member_id.subcity_id.city_id.bypass_plannig:
                        if wizard.member_id.gender == 'Male':
                            plan_city.registered_male += 1
                            plan_city.total_registered += 1
                        if wizard.member_id.gender == 'Female':
                            plan_city.registered_female += 1
                            plan_city.total_registered += 1

                        for field in plan_city.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.member_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                        raise UserError(_("Please Create an Approved City Plan For Member"))
                    plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.member_id.subcity_id.id)])
                    subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_subcity and not wizard.member_id.subcity_id.bypass_plannig:
                        if wizard.member_id.gender == 'Male':
                            plan_subcity.registered_male += 1
                            plan_subcity.total_registered += 1
                        if wizard.member_id.gender == 'Female':
                            plan_subcity.registered_female += 1
                            plan_subcity.total_registered += 1 


                        for field in plan_subcity.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.member_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                    plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.member_id.wereda_id.id)])
                    wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                    if plan_woreda and not wizard.member_id.wereda_id.bypass_plannig:
                        if wizard.member_id.gender == 'Male':
                            plan_woreda.registered_male += 1
                            plan_woreda.total_registered += 1
                        if wizard.member_id.gender == 'Female':
                            plan_woreda.registered_female += 1
                            plan_woreda.total_registered += 1


                        for field in plan_woreda.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.member_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
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
                if self.membership_org and self.member_responsibility and self.start_of_membership:
                    wizard.member_id.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership': self.start_of_membership,
                        'stock': self.stock,
                        'national_id': self.national_id
                    })
                    user = self.env.user
                    user.notify_success("Congratulations!\n Member has been Created.", '<h4>Member Created!</h4>', True)  
                else:
                    raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))

        mail_temp = self.env.ref('members_custom.member_approval')
        mail_temp.send_mail(wizard.member_id.id)



class CreateCandidateMember(models.TransientModel):
    _name="create.from.candidate.wizard"
    _description="This model will handle the creation of members"

    candidate_id = fields.Many2one('candidate.members')
    membership_org = fields.Many2one('membership.organization')
    member_responsibility = fields.Many2one('members.responsibility', default=1, readonly=True)
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected', readonly=True)
    national_id = fields.Char(translate=True)

    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['create.from.candidate.wizard'].search([('id', '=', self.id)])
        code = self.env['ir.sequence'].next_by_code('res.partner')
        new = code[4:]
        ids = "AAPP/" + str(new) + "/" + str(wizard.candidate_id.subcity_id.name)
        partner = self.env['res.partner'].create({
            'image_1920': wizard.candidate_id.image_1920,
            'name': wizard.candidate_id.name,
            'gender': wizard.candidate_id.gender,
            'age': wizard.candidate_id.age,
            'date': wizard.candidate_id.date,
            'ethnic_group': wizard.candidate_id.ethnic_group.id,
            'education_level': wizard.candidate_id.education_level.id,
            'field_of_study_id': wizard.candidate_id.field_of_study_id.id,
            'income': wizard.candidate_id.income,
            'subcity_id': wizard.candidate_id.subcity_id.id,
            'wereda_id': wizard.candidate_id.wereda_id.id,
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
            # 'member_ids': ids

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
        if partner.phone:
            name = partner.name.split()[0] + partner.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = partner.name.split()[0] + partner.phone[-9:]
                partner.user_name = name
                partner.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                partner.user_name = name
                partner.has_user_name = True
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
        wizard.candidate_id.state = 'approved'
        wizard.candidate_id.partner_id = partner.id

        if not wizard.candidate_id.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= date.today() <= year.date_to:
                    plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                    city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_city and not wizard.candidate_id.subcity_id.city_id.bypass_plannig:
                        if wizard.candidate_id.gender == 'Male':
                            plan_city.registered_male += 1
                            plan_city.total_registered += 1
                        if wizard.candidate_id.gender == 'Female':
                            plan_city.registered_female += 1
                            plan_city.total_registered += 1

                        for field in plan_city.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.candidate_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'education':
                                if field.education_level.id == wizard.candidate_id.education_level.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'study field':
                                if field.field_of_study_id.id == wizard.candidate_id.field_of_study_id.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'membership organization':
                                if field.membership_org.id == wizard.candidate_id.membership_org.id:
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
                    plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('subcity_id', '=', wizard.candidate_id.subcity_id.id)])
                    subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_subcity and not wizard.candidate_id.subcity_id.bypass_plannig:
                        if wizard.candidate_id.gender == 'Male':
                            plan_subcity.registered_male += 1
                            plan_subcity.total_registered += 1
                        if wizard.candidate_id.gender == 'Female':
                            plan_subcity.registered_female += 1
                            plan_subcity.total_registered += 1 

                        for field in plan_subcity.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.candidate_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'education':
                                if field.education_level.id == wizard.candidate_id.education_level.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'study field':
                                if field.field_of_study_id.id == wizard.candidate_id.field_of_study_id.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'membership organization':
                                if field.membership_org.id == wizard.candidate_id.membership_org.id:
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
                    plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('wereda_id', '=', wizard.candidate_id.wereda_id.id)])
                    wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_woreda and not wizard.candidate_id.wereda_id.bypass_plannig:
                        if wizard.candidate_id.gender == 'Male':
                            plan_woreda.registered_male += 1
                            plan_woreda.total_registered += 1
                        if wizard.candidate_id.gender == 'Female':
                            plan_woreda.registered_female += 1
                            plan_woreda.total_registered += 1

                        for field in plan_woreda.field_based_planning:
                            if field.field_for_member == 'ethnic':
                                if field.ethnic_group.id == wizard.candidate_id.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'education':
                                if field.education_level.id == wizard.candidate_id.education_level.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'study field':
                                if field.field_of_study_id.id == wizard.candidate_id.field_of_study_id.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_member == 'membership organization':
                                if field.membership_org.id == wizard.candidate_id.membership_org.id:
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
                if self.membership_org and self.member_responsibility and self.start_of_membership:
                    partner.write({
                        'membership_org': self.membership_org.id,
                        'member_responsibility': self.member_responsibility.id,
                        'start_of_membership': self.start_of_membership,
                        'stock': self.stock,
                        'national_id': self.national_id
                    })
                    user = self.env.user
                    user.notify_success("Congratulations!\n Member has been Created.", '<h4>Member Created!</h4>', True)  
                else:
                    raise UserError(_("Please Add All The Required Fields")) 
        else:
            raise UserError(_("Please Add A National ID"))

        mail_temp = self.env.ref('members_custom.candidate_approval')
        mail_temp.send_mail(wizard.candidate_id.id)
        wizard.candidate_id.deactivate_activity(wizard.candidate_id)
