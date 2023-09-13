"""This file will deal with the candidate members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ethiopian_date import EthiopianDateConverter

class CandidateMembers(models.Model):
    _name="candidate.members"
    _description="Candidate Approval"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(required=True, translate=True, track_visibility='onchange', store=True, size=128)
    first_name  = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    father_name = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    grand_father_name = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    age = fields.Integer(store=True, compute="_chnage_age")
    date = fields.Date(index=True, store=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True, store=True)
    ethnic_group = fields.Many2one('ethnic.groups', store=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    other_job_trainings = fields.Char(translate=True)
    source_of_livelihood = fields.Selection(selection=[('governmental', 'Governmental'), ('private', 'Private'), ('individual', 'Individual'), ('stay at home', 'Stay At Home')])
    income = fields.Float(store=True)
    work_experience_ids = fields.One2many('work.experience', 'candidate_id')
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    residential_subcity_id = fields.Many2one('membership.handlers.parent', required=True, track_visibility='onchange')
    residential_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', residential_subcity_id), ('is_special_woreda', '=', False)]", required=True, track_visibility='onchange')
    residential_subcity = fields.Char(string="Residential Subcity", required=True, store=True)
    residential_wereda = fields.Char(string="Residential Woreda", required=True)
    house_number = fields.Char()
    house_phone_number = fields.Char()
    educational_history = fields.One2many('education.history', 'candidate_id')
    office_phone_number = fields.Char()
    phone = fields.Char(track_visibility='onchange')
    previous_membership = fields.Boolean(default=False, string="Previous Political Membership")
    partner_id = fields.Many2one('res.partner', readonly=True)
    attachment_amount = fields.Integer(compute="_count_attachments")
    state = fields.Selection(selection=[('new', 'New'), ('waiting for approval', 'Waiting For Approval'), ('postponed', 'Postponed'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='new', required=True, track_visibility='onchange')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    becomes_member_on = fields.Date(string="Becomes Member On", track_visibility='onchange')
    active = fields.Boolean(default=True, track_visibility='onchange')
    archive_ids = fields.One2many('archived.information', 'candidate_id')
    supporter_id = fields.Many2one('supporter.members', store=True, readonly=True)
    note_id = fields.Text(translate=True)
    email_address = fields.Char()
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True, size=64)
    saved = fields.Boolean(default=False)
    is_lessthan_18 = fields.Boolean(default=False)
    click_counter = fields.Integer()
    main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]")



    @api.model
    def create(self, vals):
        """This function will compute the becomes_member_on"""
        phone_exists = self.env['candidate.members'].search([('phone', '=', vals['phone'])])
        # if phone_exists:
        #     raise UserError(_("A Candidate with ID = %s  the same phone already exists, Please make sure it isn't a duplicated information") % (phone_exists.id))
        # exists = self.env['candidate.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone']), ('date', '=', vals['date'])])
        # if exists:
        #     raise UserError(_("A Candidate with ID = %s the same Name, Gender and Phone already exists, Please make sure it isn't a duplicated data") % (exists.id))
        res = super(CandidateMembers, self).create(vals)
        res.becomes_member_on = res.create_date + relativedelta(months=6) 
        return res

    def unlink(self):
        """This function will delete candidate who are only in new state"""
        for record in self:
            if record.saved == True:
                raise UserError(_("You Can Only Archive Candidates"))
        return super(CandidateMembers, self).unlink()



    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'age' in fields:
            fields.remove('age')
        return super(CandidateMembers, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def deactivate_activity(self, record):
        """This function will deactivate an activity"""
        model = self.env['ir.model'].search([('model', '=', 'candidate.members'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Candidate Approval')], limit=1)
        activity = self.env['mail.activity'].search([('res_id', '=', record.id), ('res_model_id', '=', model.id), ('activity_type_id', '=', activity_type.id)])
        activity.unlink()


    def make_birthday_change_for_candidate(self):
        """This function will increase birthdays every year"""
        today = date.today()
        candidates = self.env['candidate.members'].search([]).filtered(lambda rec: rec.date != False).filtered(lambda rec: rec.date.month == today.month).filtered(lambda rec: rec.date.day == today.day)
        age_limit = self.env['age.range'].search([('for_which_stage', '=', 'candidate')])
        for candidate in candidates:
            if age_limit.minimum_age_allowed <= candidate.age <= age_limit.maximum_age_allowed:
                if candidate.age < (today.year - candidate.date.year):
                    candidate.age += 1
            if candidate.age < 18:
                candidate.is_lessthan_18 = True
            else:
                candidate.is_lessthan_18 = False

    def send_notification_to_woreda_manager(self):
        """This function will alert a woreda manager for candidate approval"""
        all_candidate = self.env['candidate.members'].search([('becomes_member_on', '=', date.today()), ('state', 'in', ['new', 'postponed'])])
        for candidate in all_candidate:
            cell_admin = candidate.cell_id.cell_admin
            candidate.write({'state': 'waiting for approval'})
            message =  _("%s's 6 month is Today. Please make a decision about the state of their Membership.") % (str(candidate.name))
            title = _("<h4>Candidate Approval</h4>")
            model = self.env['ir.model'].search([('model', '=', 'candidate.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Candidate Approval')], limit=1)
            if cell_admin:
                activity = self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Candidate Approval",
                    'date_deadline': date.today() + relativedelta(month=2),
                    'user_id': cell_admin.id,
                    'res_model_id': model.id,
                    'res_id': candidate.id,
                    'activity_type_id': activity_type.id
                })
                cell_admin.notify_warning(message, title, True)
            else:
                raise UserError(_("The Cell Doesn't Have Cell Leader To Send Activity To"))

    def send_approval(self):
        """This function will send approval of candidate to cells and Basic Organization"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Send To Basic Organization and Cell"))
            main_admin = record.main_office_id.main_admin
            message =  _("%s's 6 month is Due. Please Make A Decision About The State of Their Membership.") % (str(record.name))
            title = _("<h4>Candidate Approval</h4>")
            model = self.env['ir.model'].search([('model', '=', 'candidate.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Candidate Approval')], limit=1)
            if main_admin:
                activity = self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Candidate Approval",
                    'date_deadline': date.today() + relativedelta(month=2),
                    'user_id': main_admin.id,
                    'res_model_id': model.id,
                    'res_id': record.id,
                    'activity_type_id': activity_type.id
                })
                main_admin.notify_warning(message, title, True)
                message_dos = _("Successfully Sent")
                title_dos = _("Sent")
                self.env.user.notify_success(message_dos, title_dos, True)
            else:
                raise UserError(_("The Basic Organization Doesn't Have Basic Organization Leader To Send Activity To"))


    @api.onchange('name', 'user_input')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Name"))

            if record.user_input:
                for st in record.user_input:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in User Input"))

    @api.onchange('email_address')
    def _validate_email_address(self):
        """This function will validate the email given"""
        for record in self:
            if record.email_address:
                if '@' not in record.email_address or '.' not in record.email_address:
                    raise UserError(_("A Valid Email Address has '@' and '.'"))

    @api.onchange('subcity_id')
    def _change_all_field_for_candidate(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False

    @api.onchange('residential_subcity_id')
    def _change_all_residential_field_for_candidate(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.residential_subcity_id:
                if record.residential_subcity_id.id != record.residential_wereda_id.parent_id.id:
                    record.residential_wereda_id = False

    def _count_attachments(self):
        """This function will count the number of attachments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0

    @api.onchange('becomes_member_on')
    def _check_date(self):
        """This function will check if the date being set is the correct one"""
        for record in self:
            if not record.becomes_member_on and record.create_date:
                raise UserError(_("Please Add The Date When The Candidate Becomes a Member"))
            if record.becomes_member_on and record.create_date:
                if record.becomes_member_on < record.create_date.date():
                    raise UserError(_("Please Pick A Date That Is After The Created Date %s") % (record.create_date))


    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.candidate.wizard'].create({
            'candidate_id': self.id
        })
        return {
            'name': _('Why Do You Want To Archive This Record?'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.candidate.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'context': {'active_id': self.id}
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            record.active = True
            record.supporter_id.active = True
            all_archived = self.env['archived.information'].search([('candidate_id', '=', record.id)])
            for archive in all_archived:
                if archive.archived:
                    archive.archived = False
                    archive.date_to = date.today()


    def postpone_approval(self):
        """This function will postpone decision"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Postponement."))
            # elif record.click_counter > record.attachment_amount + 1:
            #     raise ValidationError(_("PLEASE READ THE ERROR\n\n\n\n!!!!!Please Add An Attachment To Justify Postponement."))
            #     record.click_counter = record.attachment_amount + 1
            else:
                record.state = 'postponed'
            mail_temp = self.env.ref('members_custom.candidate_postpone')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)


    def deny_membership(self):
        """This function will return state to new"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify As To Why You Want To Deny Membership To This Candidate"))
            # elif record.click_counter > record.attachment_amount + 1:
            #     raise ValidationError(_("PLEASE READ THE ERROR\n\n\n\n!!!!!Please Give A Reason In The Note Section As To Why You Want To Deny Membership To This Candidate"))
            #     record.click_counter = record.attachment_amount + 1
            else:
                record.state = 'rejected'
            mail_temp = self.env.ref('members_custom.candidate_denial')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)


    def back_to_new(self):
        """This function will return state of Candidate to new"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Returning Candidacy!!"))
            # elif record.click_counter > record.attachment_amount + 1:
            #     raise ValidationError(_("PLEASE READ THE ERROR\n\n\n\n!!!!!Please Give A Reason In The Note Section As To Why You Want To Deny Membership To This Candidate"))
            #     record.click_counter = record.attachment_amount + 1
            else:
                record.state = 'new'
                record.becomes_member_on = date.today() + relativedelta(months=6) 
                mail_temp = self.env.ref('members_custom.candidate_revival')
                mail_temp.send_mail(record.id)
                self.deactivate_activity(record)

    @api.onchange('source_of_livelihood')
    def _remove_data(self):
       """This function will remove data if source_of_livelihood is stay at home"""
       for record in self:
           if record.source_of_livelihood == 'stay at home':
               for jobs in record.work_experience_ids:
                   jobs.current_job = False


    @api.onchange('income')
    def _validate_income(self):
        """This function will check if income is positive or not"""
        for record in self:
            if record.income:
                if record.income < 0.00:
                    raise UserError(_("Income Can't Be Negative"))

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                phone_exists = self.env['candidate.members'].search([('phone', '=', record.phone)])
                if phone_exists:
                    raise UserError(_("A Candidate with the same phone already exists, Please make sure it isn't a duplicated information"))
                for st in record.phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))


    @api.onchange('house_phone_number')
    def _proper_house_phone_number(self):
        """This function will check if house_phone_number is of proper format"""
        for record in self:
            if record.house_phone_number:
                for st in record.house_phone_number:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in an House Phone Number"))
                if record.house_phone_number[0] != '0':
                    raise UserError(_("A Valid House Phone Number Starts With 0"))
                if len(record.house_phone_number) != 10:
                    raise UserError(_("A Valid House Phone Number Has 10 Digits"))

    @api.onchange('office_phone_number')
    def _proper_office_phone_number(self):
        """This function will check if house_phone_number is of proper format"""
        for record in self:
            if record.office_phone_number:
                for st in record.office_phone_number:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in an Office Phone Number"))
                if record.office_phone_number[0] != '0':
                    raise UserError(_("A Valid Office Phone Number Starts With 0"))
                if len(record.office_phone_number) != 10:
                    raise UserError(_("A Valid Office Phone Number Has 10 Digits"))


    # @api.depends('date')
    # def _chnage_age(self):
    #     """This function will change the age of person based on date"""
    #     for record in self:
    #         if record.date:
    #             age_limit = self.env['age.range'].search([('for_which_stage', '=', 'candidate')])
    #             if not age_limit:
    #                 raise UserError(_("Please Set Age Limit for Candidate in the Configuration"))
    #             today = date.today()
    #             if record.date >= today:
    #                 raise UserError(_("You Have To Pick A Date Before Today."))
    #             if today.month < record.date.month:
    #                 record.age = (today.year - record.date.year) - 1
    #                 if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
    #                     raise UserError(_("This Age isn't within the Age Limit Range given for Candidate"))
    #             else:
    #                 if today.month == record.date.month and today.day < record.date.day:
    #                     record.age = (today.year - record.date.year) - 1
    #                     if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
    #                         raise UserError(_("This Age isn't within the Age Limit Range given for Candidate"))
    #                 else:
    #                     record.age = today.year - record.date.year
    #                     if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
    #                         raise UserError(_("This Age isn't within the Age Limit Range given for Candidate"))



    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 34:
                    record.is_user_input = False
                else:
                    record.is_user_input = True


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'approved' or record.state == 'rejected'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def create_members(self):
        """This function will create members from candidates"""
        for record in self:

            age_limit = self.env['age.range'].search([('for_which_stage', '=', 'member')])
            if not age_limit:
                raise UserError(_("Please Set Age Limit for Member in the Configuration"))
            if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
                raise UserError(_("This Age isn't within the Age Limit Range given for Members"))

            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Approval."))


            wizard = self.env['create.from.candidate.wizard'].create({
                'candidate_id': record.id,
                'main_office_id': record.main_office_id.id,
                'cell_id': record.cell_id.id,
                'wereda_id': record.wereda_id.id,
            })
            return {
                'name': _('Create Members From Candidate'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.from.candidate.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }
        
    def create_league(self):
        """This function will create leagues from membership"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Approval."))
            else:
                partner = self.env['res.partner'].create({
                    'image_1920': record.image_1920,
                    'name': record.name,
                    'first_name': record.first_name,
                    'father_name': record.father_name,
                    'grand_father_name': record.grand_father_name,
                    'age': record.age,
                    'date': record.date,
                    'gender': record.gender,
                    'ethnic_group': record.ethnic_group.id,
                    'education_level': record.education_level.id,
                    'field_of_study_id': record.field_of_study_id.id,
                    'subcity_id': record.subcity_id.id,
                    'wereda_id': record.wereda_id.id,
                    'residential_subcity_id': record.residential_subcity_id.id,
                    'residential_wereda_id': record.residential_wereda_id.id,
                    'email_address': record.email_address,
                    'is_user_input': record.is_user_input,
                    'user_input': record.user_input,
                    'phone': record.phone
                })


                wizard = self.env['create.league.wizard'].create({
                    'league_id': partner.id,
                    'candidate_id': record.id,
                    'main_office_id': record.main_office_id.id,
                    'cell_id': record.cell_id.id,
                    'wereda_id': record.wereda_id.id,
                })
                return {
                    'name': _('Create League Wizard'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'create.league.wizard',
                    'view_mode': 'form',
                    'res_id': wizard.id,
                    'target': 'new'
                    }