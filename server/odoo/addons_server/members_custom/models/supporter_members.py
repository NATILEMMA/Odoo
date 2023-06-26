"""This file will deal with the handling of supporter members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import http


class SupportingMembers(models.Model):
    _name="supporter.members"
    _description="Supporter Approval"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(translate=True, required=True, track_visibility='onchange', store=True)
    date = fields.Date(string="Date of Birth", store=True)
    age = fields.Integer(copy=False, readonly=True, store=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], required=True, store=True)
    ethnic_group = fields.Many2one('ethnic.groups', required=True, store=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    work_place = fields.Char(translate=True, copy=False)
    position = fields.Char(translate=True, copy=False)
    income = fields.Float(track_visibility='onchange')
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    house_number = fields.Char(translate=True)
    educational_history = fields.One2many('education.history', 'supporter_id')
    phone = fields.Char(track_visibility='onchange')
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', track_visibility='onchange')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False)
    start_of_support = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Supporter Start Year')
    attachment_amount = fields.Integer(compute="_count_attachments")
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    state = fields.Selection(selection=[('new', 'New'), ('waiting for approval', 'Waiting For Approval'), ('postponed', 'Postponed'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='new', required=True, track_visibility='onchange')
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    active = fields.Boolean(default=True, track_visibility='onchange')
    archive_ids = fields.One2many('archived.information', 'supporter_id')
    becomes_a_candidate_on = fields.Date(string="Becomes A Candidate On", track_visibility='onchange')
    note_id = fields.Text(translate=True)
    email_address = fields.Char()
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True)
    saved = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        exists = self.env['supporter.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone'])])
        if exists:
            raise UserError(_("A supporter with the same name, gender and phone already exists, Please make sure it isn't a duplicated data"))
        res = super(SupportingMembers, self).create(vals)
        res.becomes_a_candidate_on = res.create_date + relativedelta(months=3)
        res.state = 'new'
        res.saved = True
        if not res.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= res.create_date.date() <= year.date_to:
                    plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
                    city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                    if plan_city and not res.subcity_id.city_id.bypass_plannig:
                        if res.gender == 'Male':
                            plan_city.registered_male += 1
                            plan_city.total_registered += 1
                        if res.gender == 'Female':
                            plan_city.registered_female += 1
                            plan_city.total_registered += 1

                        for field in plan_city.field_based_planning:
                            if field.field_for_candidate_supporter == 'ethnic':
                                if field.ethnic_group.id == res.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_candidate_supporter == 'education':
                                if field.education_level.id == res.education_level.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_candidate_supporter == 'study field':
                                if field.field_of_study_id.id == res.field_of_study_id.id:
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
                        raise UserError(_("Please Create an Approved City Plan For Supporter"))
                    plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('subcity_id', '=', res.subcity_id.id)])
                    subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                    if plan_subcity and not res.subcity_id.bypass_plannig:
                        if res.gender == 'Male':
                            plan_subcity.registered_male += 1
                            plan_subcity.total_registered += 1
                        if res.gender == 'Female':
                            plan_subcity.registered_female += 1
                            plan_subcity.total_registered += 1

                        for field in plan_subcity.field_based_planning:
                            if field.field_for_candidate_supporter == 'ethnic':
                                if field.ethnic_group.id == res.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_candidate_supporter == 'education':
                                if field.education_level.id == res.education_level.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_candidate_supporter == 'study field':
                                if field.field_of_study_id.id == res.field_of_study_id.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100

                        plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100 
                        subcity_report.registered += 1
                        subcity_report.accomplished = (subcity_report.registered / plan_subcity.total_estimated) * 100
                        if 30 <= plan_subcity.accomplished <= 50.00:
                            plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
                            for plan in plan_subcities:
                                if plan.accomplished < 30:
                                    plan.colors = 'red'
                            plan_subcity.colors = 'orange'
                        if 50 < plan_subcity.accomplished < 75:
                            plan_subcity.colors = 'blue'
                        if plan_subcity.accomplished >= 75:
                            plan_subcity.colors = 'green'
                    else:
                        raise UserError(_("Please Create an Approved Sub City Plan For Supporter"))
                    plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('wereda_id', '=', res.wereda_id.id)])
                    wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                    if plan_woreda and not res.wereda_id.bypass_plannig:
                        if res.gender == 'Male':
                            plan_woreda.registered_male += 1
                            plan_woreda.total_registered += 1
                        if res.gender == 'Female':
                            plan_woreda.registered_female += 1
                            plan_woreda.total_registered += 1

                        for field in plan_woreda.field_based_planning:
                            if field.field_for_candidate_supporter == 'ethnic':
                                if field.ethnic_group.id == res.ethnic_group.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_candidate_supporter == 'education':
                                if field.education_level.id == res.education_level.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                            if field.field_for_candidate_supporter == 'study field':
                                if field.field_of_study_id.id == res.field_of_study_id.id:
                                    field.total_registered += 1
                                    field.accomplished = (field.total_registered / field.total_estimated) * 100
                                    
                        plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                        wereda_report.registered += 1
                        wereda_report.accomplished = (wereda_report.registered / plan_woreda.total_estimated) * 100
                        if 30 <= plan_woreda.accomplished <= 50.00:
                            plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
                            for plan in plan_woredas:
                                if plan.accomplished < 30:
                                    plan.colors = 'red'
                            plan_woreda.colors = 'orange'
                        if 50 < plan_woreda.accomplished < 75:
                            plan_woreda.colors = 'blue'
                        if plan_woreda.accomplished >= 75:
                            plan_woreda.colors = 'green'
                    else:
                        raise UserError(_("Please Create an Approved Woreda Plan For Supporter"))
                user = self.env.user
                user.notify_success("Congratulations!\n Supporter has been Created.", '<h4>Supporter Created!</h4>', True)  
            else:
                raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))

        return res


    def unlink(self):
        """This function will delete supporter who are only in new state"""
        for record in self:
            if record.state != 'new':
                raise UserError(_("You Can Only Delete Supporters Who Are In New State"))
        return super(SupportingMembers, self).unlink()


    def deactivate_activity(self, record):
        """This function will deactivate an activity"""
        model = self.env['ir.model'].search([('model', '=', 'supporter.members'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Supporter Approval')], limit=1)
        activity = self.env['mail.activity'].search([('res_id', '=', record.id), ('res_model_id', '=', model.id), ('activity_type_id', '=', activity_type.id)])
        activity.unlink()

    @api.model
    def date_convert_and_set(self,picked_date):
        for record in self:
            if record:    
                return record
            else:
                return False

    def make_birthday_change_for_supporter(self):
        """This function will increase birthdays every year"""
        today = date.today()
        supporters = self.env['supporter.members'].search([]).filtered(lambda rec: rec.date != False).filtered(lambda rec: rec.date.month == today.month).filtered(lambda rec: rec.date.day == today.day)
        for supporter in supporters:
            if supporter.age < (today.year - supporter.date.year):
                supporter.age += 1


    def send_notification_to_woreda_manager_for_supporter(self):
        """This function will alert a woreda manager for supporter approval"""
        all_supporter = self.env['supporter.members'].search([('becomes_a_candidate_on', '=', date.today()), ('state', 'in', ['new', 'postponed'])])
        for supporter in all_supporter:
            wereda_manager = supporter.wereda_id.branch_manager
            supporter.write({'state': 'waiting for approval'})
            message = str(supporter.name) + "'s 3 month is Today. Please Make A Decision About The State of Their Candidacy."
            model = self.env['ir.model'].search([('model', '=', 'supporter.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Supporter Approval')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Supporter Approval",
                'date_deadline': date.today() + relativedelta(month=2),
                'user_id': wereda_manager.id,
                'res_model_id': model.id,
                'res_id': supporter.id,
                'activity_type_id': activity_type.id
            })
            wereda_manager.notify_warning(message, '<h4>Supporter Approval</h4>', True)

    def send_approval(self):
        """This function will send approval of candidate to cells and Main Office"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Send To Main Office and Cell"))
            wizard = self.env['send.supporters'].create({
                'wereda_id': record.wereda_id.id,
                'supporter_id': record.id
            })
            return {
                'name': _('Transfer Supporter Approval Decision'),
                'type': 'ir.actions.act_window',
                'res_model': 'send.supporters',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }


    @api.onchange('age')
    def _all_must_be_more_than_15(self):
        """This function will check if the age of the supporter is above 15"""
        for record in self:
            if record.age:
                if record.age < 15:
                    raise UserError(_("The Supporter's Age Must Be Above 15"))

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                if len(record.phone) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.phone[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......')) 


    @api.onchange('subcity_id')
    def _change_all_field_for_supporter(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False


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

    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 101:
                    record.is_user_input = False
                else:
                    record.is_user_input = True


    @api.onchange('becomes_a_candidate_on')
    def _check_date(self):
        """This function will check if the date being set is the correct one"""
        for record in self:
            if record.becomes_a_candidate_on and record.create_date:
                if record.becomes_a_candidate_on < record.create_date.date():
                    message = "Please Pick A Date That Is After The Created Date " + str(record.create_date.strftime("%m/%d/%Y"))
                    raise UserError(_(message))



    def add_attachment(self):
        """This function will add attachments"""
        for record in self:
            wizard = self.env['attachment.wizard'].create({
                'res_id': record.id,
                'res_model': 'supporter.members'
            })
            return {
                'name': _('Create Attachment'),
                'type': 'ir.actions.act_window',
                'res_model': 'attachment.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }

    def _count_attachments(self):
        """This function will count the number of attachments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0


    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.supporter.wizard'].create({
            'supporter_id': self.id
        })
        return {
            'name': _('Why Do You Want To Archive This Record?'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.supporter.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            record.active = True
            all_archived = self.env['archived.information'].search([('supporter_id', '=', record.id)])
            for archive in all_archived:
                if archive.archived:
                    archive.archived = False
                    archive.date_to = date.today()

    def postpone_approval(self):
        """This function will postpone decision"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Justify Postponement."))
            else:
                record.state = 'postponed'
            mail_temp = self.env.ref('members_custom.supporter_postpone')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)


    def deny_candidancy(self):
        """This function will return state to new"""
        for record in self:
            if record.note_id == False:
                raise ValidationError(_("Please Give A Reason In The Note Section As To Why You Want To Deny Candidacy To This Supporter"))
            else:
                record.state = 'rejected'
            mail_temp = self.env.ref('members_custom.supporter_denial')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'approved' or record.state == 'rejected'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def create_candidate(self):
        # """This function will create candidates from supporters"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Justify Approval."))
            candidate = self.env['candidate.members'].sudo().create({
                'image_1920': record.image_1920,
                'name': record.name,
                'age': record.age,
                'gender': record.gender,
                'date': record.date,
                'education_level': record.education_level.id,
                'field_of_study_id': record.field_of_study_id.id,
                'ethnic_group': record.ethnic_group.id,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'house_number': record.house_number,
                'phone': record.phone,
                'income': record.income,
                'supporter_id': record.id,
                'email_address': record.email_address,
                'is_user_input': record.is_user_input,
                'user_input': record.user_input,
                'saved': True
            })
            for ed in record.educational_history:
                candidate.write({
                    'educational_history': [(0, 0, {
                        'education_level': ed.education_level.id,
                        'field_of_study_id': ed.field_of_study_id.id,
                        'candidate_id': candidate.id
                    })],
                })
            if record.work_place and record.position:
                candidate.write({
                    'work_experience_ids': [(0, 0, {
                        'name': record.position,
                        'place_of_work': record.work_place,
                        'current_job': True
                    })],
                })
            if not record.subcity_id.city_id.bypass_plannig:
                year = self.env['fiscal.year'].search([('state', '=', 'active')])
                if year:
                    if year.date_from <= date.today() <= year.date_to:
                        plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                        city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_city and not record.subcity_id.city_id.bypass_plannig:
                            if record.gender == 'Male':
                                plan_city.registered_male += 1
                                plan_city.total_registered += 1
                            if record.gender == 'Female':
                                plan_city.registered_female += 1
                                plan_city.total_registered += 1

                            for field in plan_city.field_based_planning:
                                if field.field_for_candidate_supporter == 'ethnic':
                                    if field.ethnic_group.id == record.ethnic_group.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_candidate_supporter == 'education':
                                    if field.education_level.id == record.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_candidate_supporter == 'study field':
                                    if field.field_of_study_id.id == record.field_of_study_id.id:
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
                            raise UserError(_("Please Create an Approved City Plan For Candidate"))
                        plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('subcity_id', '=', record.subcity_id.id)])
                        subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                        if plan_subcity and not record.subcity_id.bypass_plannig:
                            if record.gender == 'Male':
                                plan_subcity.registered_male += 1
                                plan_subcity.total_registered += 1
                            if record.gender == 'Female':
                                plan_subcity.registered_female += 1
                                plan_subcity.total_registered += 1 

                            for field in plan_subcity.field_based_planning:
                                if field.field_for_candidate_supporter == 'ethnic':
                                    if field.ethnic_group.id == record.ethnic_group.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_candidate_supporter == 'education':
                                    if field.education_level.id == record.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_candidate_supporter == 'study field':
                                    if field.field_of_study_id.id == record.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100

                            plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                            subcity_report.registered += 1
                            subcity_report.accomplished = (subcity_report.registered / plan_subcity.total_estimated) * 100
                            if 30 <= plan_subcity.accomplished <= 50.00:
                                plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                                for plan in plan_subcities:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_subcity.colors = 'orange'
                            if 50 < plan_subcity.accomplished < 75:
                                plan_subcity.colors = 'blue'
                            if plan_subcity.accomplished >= 75:
                                plan_subcity.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Sub City Plan For Candidate"))
                        plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('wereda_id', '=', record.wereda_id.id)])
                        wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_woreda and not record.wereda_id.bypass_plannig:
                            if record.gender == 'Male':
                                plan_woreda.registered_male += 1
                                plan_woreda.total_registered += 1
                            if record.gender == 'Female':
                                plan_woreda.registered_female += 1
                                plan_woreda.total_registered += 1

                            for field in plan_woreda.field_based_planning:
                                if field.field_for_candidate_supporter == 'ethnic':
                                    if field.ethnic_group.id == record.ethnic_group.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_candidate_supporter == 'education':
                                    if field.education_level.id == record.education_level.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100
                                if field.field_for_candidate_supporter == 'study field':
                                    if field.field_of_study_id.id == record.field_of_study_id.id:
                                        field.total_registered += 1
                                        field.accomplished = (field.total_registered / field.total_estimated) * 100

                            plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                            wereda_report.registered += 1
                            wereda_report.accomplished = (wereda_report.registered / plan_woreda.total_estimated) * 100
                            if 30 <= plan_woreda.accomplished <= 50.00:
                                plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                                for plan in plan_woredas:
                                    if plan.accomplished < 30:
                                        plan.colors = 'red'
                                plan_woreda.colors = 'orange'
                            if 50 < plan_woreda.accomplished < 75:
                                plan_woreda.colors = 'blue'
                            if plan_woreda.accomplished >= 75:
                                plan_woreda.colors = 'green'
                        else:
                            raise UserError(_("Please Create an Approved Woreda Plan For Candidate"))
                    record.candidate_id = candidate
                    record.state = 'approved'
                    mail_temp = self.env.ref('members_custom.supporter_approval')
                    mail_temp.send_mail(record.id)
                    self.deactivate_activity(record)
                    user = self.env.user
                    user.notify_success("Congratulations!\n Candidate has been Created.", '<h4>Candidate Created!</h4>', True)  
                else:
                    raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))