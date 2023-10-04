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


    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years


    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(track_visibility='onchange', store=True, size=128, translate=True)
    first_name  = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    father_name = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    grand_father_name = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    date = fields.Date(string="Date of Birth")
    age = fields.Integer(store=True, compute="_chnage_age")
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], required=True, store=True)
    ethnic_group = fields.Many2one('ethnic.groups', required=True, store=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    work_place = fields.Char(translate=True, copy=False, size=64)
    position = fields.Char(translate=True, copy=False, size=64)
    income = fields.Float(track_visibility='onchange')
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    residential_subcity = fields.Char(string="Residential Subcity", required=True, store=True)
    residential_wereda = fields.Char(string="Residential Woreda", required=True)
    house_number = fields.Char(translate=True)
    phone = fields.Char(track_visibility='onchange', required=True)
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', track_visibility='onchange', required=True)
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False, size=64)
    start_of_support = fields.Selection(selection=_default_years, string='Supporter Start Year')
    attachment_amount = fields.Integer(compute="_count_attachments")
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    state = fields.Selection(selection=[('draft', 'Draft'), ('new', 'New'), ('waiting for approval', 'Waiting For Approval'), ('postponed', 'Postponed'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='new', required=True, track_visibility='onchange')
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    active = fields.Boolean(default=True, track_visibility='onchange')
    becomes_a_candidate_on = fields.Date(string="Becomes A Candidate On", track_visibility='onchange')
    note_id = fields.Text(translate=True)
    email_address = fields.Char()
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True, size=64)
    saved = fields.Boolean(default=False)
    year_of_payment = fields.Many2one("fiscal.year", string='Year', store=True)
    is_lessthan_18 = fields.Boolean(default=False)
    click_counter = fields.Integer()
    main_office_id = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_office_id)]")



    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        # NAME CORRECTION
        vals['name'] = vals['first_name'] + " " + vals['father_name'] + " " + vals['grand_father_name']

        # PHONE DUPLICATION BEING CHECKED
        # phone_exists = self.env['supporter.members'].search([('phone', '=', vals['phone'])])
        # if phone_exists:
        #     raise UserError(_("A Supporter with ID %s with the same phone already exists, Please make sure it isn't a duplicated information") % (phone_exists.id))

        # SUPPORTER DUPLICATION BEING CHECKED
        # exists = self.env['supporter.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone']), ('date', '=', vals['date'])])
        # if exists:
        #     raise UserError(_("A Supporter with ID %s with the same name, gender and phone already exists, Please make sure it isn't a duplicated data") % (exists.id))
        
        # SUPPORTER CREATED WITH STATE, BECOMES CANDIDATE ON, AGE AND DATE VALIDATION
        res = super(SupportingMembers, self).create(vals)
        res.becomes_a_candidate_on = res.create_date + relativedelta(months=3)
        if res.state == 'draft':
            res.saved = False
        if res.state == 'new':
            res.saved = True
            mail_temp = self.env.ref('member_registration.supporter_acceptance')
            mail_temp.send_mail(res.id)
        if res.age < 18:
            res.is_lessthan_18 = True
        else:
            res.is_lessthan_18 = False
        if res.date == False or res.age == 0:
            raise UserError(_("You Have To Pick A Date to set Age of the Supporter"))

        # ADDING SUPPORTER IN CELL
        if res.cell_id:
            all_supporters = res.cell_id.supporter_ids.ids + [res.id]
            res.cell_id.supporter_ids = [(5, 0, 0)]
            res.cell_id.supporter_ids = [(6, 0, all_supporters)]

        # ADDING SUPPORTER INTO ANNUAL PLAN OF CITY, SUBCITY AND WOREDA
        if not res.subcity_id.city_id.bypass_plannig:
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year:
                if year.date_from <= res.create_date.date() <= year.date_to:
                    if not res.subcity_id.city_id.bypass_plannig:
                        plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
                        city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                        if plan_city:
                            if res.gender == 'Male':
                                plan_city.registered_male += 1
                                plan_city.total_registered += 1
                            if res.gender == 'Female':
                                plan_city.registered_female += 1
                                plan_city.total_registered += 1

                            for field in plan_city.field_based_planning:
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
                    if not res.subcity_id.bypass_plannig:
                        plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('subcity_id', '=', res.subcity_id.id)])
                        subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                        if plan_subcity:
                            if res.gender == 'Male':
                                plan_subcity.registered_male += 1
                                plan_subcity.total_registered += 1
                            if res.gender == 'Female':
                                plan_subcity.registered_female += 1
                                plan_subcity.total_registered += 1

                            for field in plan_subcity.field_based_planning:
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
                    if not res.wereda_id.bypass_plannig:
                        plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('wereda_id', '=', res.wereda_id.id)])
                        wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])            
                        if plan_woreda:
                            if res.gender == 'Male':
                                plan_woreda.registered_male += 1
                                plan_woreda.total_registered += 1
                            if res.gender == 'Female':
                                plan_woreda.registered_female += 1
                                plan_woreda.total_registered += 1

                            for field in plan_woreda.field_based_planning:
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
            else:
                raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))

        # SENDING CREATION CONFIRMATION MESSAGE 
        user = self.env.user
        message = _("Congratulations!\n Supporter has been Created.")
        title = _("<h4>Supporter Created!</h4>")
        user.notify_success(message, title, True)  
        return res


    def unlink(self):
        """This function will delete supporter who are only in new state"""
        for record in self:
            if record.saved == True:
                raise UserError(_("You Can Only Archive Supporters"))
        return super(SupportingMembers, self).unlink()


    def deactivate_activity(self, record):
        """This function will deactivate an activity"""
        model = self.env['ir.model'].search([('model', '=', 'supporter.members'), ('is_mail_activity', '=', True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Supporter Approval')], limit=1)
        activity = self.env['mail.activity'].search([('res_id', '=', record.id), ('res_model_id', '=', model.id), ('activity_type_id', '=', activity_type.id)])
        activity.unlink()


    def make_birthday_change_for_supporter(self):
        """This function will increase birthdays every year"""
        today = date.today()
        supporters = self.env['supporter.members'].search([]).filtered(lambda rec: rec.date != False).filtered(lambda rec: rec.date.month == today.month).filtered(lambda rec: rec.date.day == today.day)
        age_limit = self.env['age.range'].search([('for_which_stage', '=', 'supporter')])
        for supporter in supporters:
            if age_limit.minimum_age_allowed <= supporter.age <= age_limit.maximum_age_allowed:
                if supporter.age < (today.year - supporter.date.year):
                    supporter.age += 1
            if supporter.age < 18:
                supporter.is_lessthan_18 = True
            else:
                supporter.is_lessthan_18 = False


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'age' in fields:
            fields.remove('age')
        return super(SupportingMembers, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)


    def send_notification_to_woreda_manager_for_supporter(self):
        """This function will alert a woreda manager for supporter approval"""
        all_supporter = self.env['supporter.members'].search([('becomes_a_candidate_on', '=', date.today()), ('state', 'in', ['new', 'postponed'])])
        for supporter in all_supporter:
            cell_admin = supporter.cell_id.cell_admin
            supporter.write({'state': 'waiting for approval'})
            message =  _("%s's 3 month is Today. Please Make A Decision About The State of Their Candidacy.") % (str(supporter.name))
            title = _("<h4>Supporter Approval</h4>")
            model = self.env['ir.model'].search([('model', '=', 'supporter.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Supporter Approval')], limit=1)
            if cell_admin:
                activity = self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Supporter Approval",
                    'date_deadline': date.today() + relativedelta(month=2),
                    'user_id': cell_admin.id,
                    'res_model_id': model.id,
                    'res_id': supporter.id,
                    'activity_type_id': activity_type.id
                })
                cell_admin.notify_warning(message, title, True)
            # else:
            #     raise UserError(_("The Cell Doesn't Have Cell Leader To Send Activity To"))


    def send_approval(self):
        """This function will send approval of candidate to cells and Main Office"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Send To Basic Organization"))
            main_admin = record.main_office_id.main_admin
            message =  _("%s's 3 month is Due. Please Make A Decision About The State of Their Candidacy.") % (str(record.name))
            title = _("<h4>Supporter Approval</h4>")
            model = self.env['ir.model'].search([('model', '=', 'supporter.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Supporter Approval')], limit=1)
            if main_admin:
                activity = self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Supporter Approval",
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
            # else:
            #     raise UserError(_("The Basic Organization Doesn't Have Basic Organization Leader To Send Activity To"))


    @api.onchange('name', 'gov_responsibility', 'user_input', 'position')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Name"))
    
            if record.gov_responsibility:
                for st in record.gov_responsibility:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Governmental Responsibility"))

            if record.user_input:
                for st in record.user_input:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in User Input"))

            if record.position:
                for st in record.position:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Job Position"))

    @api.onchange('email_address')
    def _validate_email_address(self):
        """This function will validate the email given"""
        for record in self:
            if record.email_address:
                if '@' not in record.email_address or '.' not in record.email_address:
                    raise UserError(_("A Valid Email Address has '@' and '.'"))

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
                phone_exists = self.env['supporter.members'].search([('phone', '=', record.phone)])
                if phone_exists:
                    raise UserError(_("A Supporter with the same phone already exists, Please make sure it isn't a duplicated information"))
                for st in record.phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))


    @api.onchange('subcity_id')
    def _change_all_field_for_supporter(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False
                    record.main_office_id = False
                    record.cell_id = False

    @api.onchange('wereda_id')
    def _change_all_field_for_supporter_from_wereda(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.wereda_id:
                if record.wereda_id.id != record.main_office_id.wereda_id.id:
                    record.main_office_id = False
                    record.cell_id = False

    @api.onchange('main_office_id')
    def _change_all_field_for_supporter_from_main_office(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.main_office_id:
                if record.main_office_id.id != record.cell_id.main_office.id:
                    record.cell_id = False

    # @api.onchange('residential_subcity_id')
    # def _change_all_residential_field_for_supporter(self):
    #     """This function will make all fields False when subcity changes"""
    #     for record in self:
    #         if record.residential_subcity_id:
    #             if record.residential_subcity_id.id != record.residential_wereda_id.parent_id.id:
    #                 record.residential_wereda_id = False


    @api.depends('date')
    def _chnage_age(self):
        """This function will change the age of person based on date"""
        for record in self:
            if record.date:
                age_limit = self.env['age.range'].search([('for_which_stage', '=', 'supporter')])
                if not age_limit:
                    raise UserError(_("Please Set Age Limit for Supporter in the Configuration"))
                today = date.today()
                if record.date >= today:
                    raise UserError(_("You Have To Pick A Date Before Today."))
                if today.month < record.date.month:
                    record.age = (today.year - record.date.year) - 1
                    if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
                        raise UserError(_("This Age isn't within the Age Limit Range given for Supporter"))
                else:
                    if today.month == record.date.month and today.day < record.date.day:
                        record.age = (today.year - record.date.year) - 1
                        if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
                            raise UserError(_("This Age isn't within the Age Limit Range given for Supporter"))
                    else:
                        record.age = today.year - record.date.year
                        if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
                            raise UserError(_("This Age isn't within the Age Limit Range given for Supporter"))


    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 34:
                    record.is_user_input = False
                else:
                    record.is_user_input = True

    @api.onchange('becomes_a_candidate_on')
    def _check_date(self):
        """This function will check if the date being set is the correct one"""
        for record in self:
            if not record.becomes_a_candidate_on and record.create_date:
                raise UserError(_("Please Add The Date When The Supporter Becomes a Candidate"))
            if record.becomes_a_candidate_on and record.create_date:
                if record.becomes_a_candidate_on < record.create_date.date():
                    raise UserError(_("Please Pick A Date That Is After The Created Date"))

    @api.onchange('year_of_payment')
    def _generate_payments(self):
        """This function will generate the payment of previous years"""
        for record in self:
            record.donation_ids = [(5, 0, 0)]
            all_donation = self.env['donation.payment'].search([('supporter_id', '=', record._origin.id), ('year', '=', record.year_of_payment.id)])
            if len(all_donation.ids) > 0:
                record.write({
                    'donation_ids': [(6, 0, all_donation.ids)]
                })

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

    def approve_supporter(self):
        """This function will approve supporter from Portal"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify As To Why You Want To Make This Individual a Supporter"))
            else:
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

    def postpone_approval(self):
        """This function will postpone decision"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount != record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Postponement."))
            else:
                record.state = 'postponed'
            mail_temp = self.env.ref('member_registration.supporter_postpone')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)


    def deny_candidancy(self):
        """This function will return state to new"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify As To Why You Want To Deny Candidacy To This Supporter"))
            else:
                record.state = 'rejected'
            mail_temp = self.env.ref('member_registration.supporter_denial')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)

    def back_to_new(self):
        """This function will return state of Supporter to new"""
        for record in self:
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Returning Supporter Title!!"))
            else:
                record.state = 'new'
                record.becomes_a_candidate_on = date.today() + relativedelta(months=3)  
                mail_temp = self.env.ref('member_registration.supporter_revival')
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

            # CHECKING ATTACHMENT BEING ADDED
            record.click_counter += 1
            if record.attachment_amount < record.click_counter:
                raise ValidationError(_("Please Add An Attachment To Justify Approval."))

            # CHECKING AGE LIMIT FOR CANDIDATE
            age_limit = self.env['age.range'].search([('for_which_stage', '=', 'candidate')])
            if not age_limit:
                raise UserError(_("Please Set Age Limit for Candidate in the Configuration"))
            if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
                raise UserError(_("This Age isn't within the Age Limit Range given for Candidate"))

            # CREATING A CANDIDATE
            candidate = self.env['candidate.members'].sudo().create({
                'image_1920': record.image_1920,
                'name': record.name,
                'first_name': record.first_name,
                'father_name': record.father_name,
                'grand_father_name': record.grand_father_name,
                'age': record.age,
                'gender': record.gender,
                'date': record.date,
                'education_level': record.education_level.id,
                'field_of_study_id': record.field_of_study_id.id,
                'ethnic_group': record.ethnic_group.id,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'main_office_id': record.main_office_id.id,
                'cell_id': record.cell_id.id,
                'residential_subcity': record.residential_subcity,
                'residential_wereda': record.residential_wereda,
                'house_number': record.house_number,
                'phone': record.phone,
                'income': record.income,
                'supporter_id': record.id,
                'email_address': record.email_address,
                'is_user_input': record.is_user_input,
                'user_input': record.user_input,
                'saved': True,
                'is_lessthan_18': record.is_lessthan_18
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

            # ADDING CANDIDATE INTO ANNUAL CITY, SUBCITY, WOREDA PLAN
            if not record.subcity_id.city_id.bypass_plannig:
                year = self.env['fiscal.year'].search([('state', '=', 'active')])
                if year:
                    if year.date_from <= date.today() <= year.date_to:
                        if not record.subcity_id.city_id.bypass_plannig:
                            plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                            city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                            if plan_city:
                                if record.gender == 'Male':
                                    plan_city.registered_male += 1
                                    plan_city.total_registered += 1
                                if record.gender == 'Female':
                                    plan_city.registered_female += 1
                                    plan_city.total_registered += 1

                                for field in plan_city.field_based_planning:
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
                        if not record.subcity_id.bypass_plannig:
                            plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('subcity_id', '=', record.subcity_id.id)])
                            subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                            if plan_subcity:
                                if record.gender == 'Male':
                                    plan_subcity.registered_male += 1
                                    plan_subcity.total_registered += 1
                                if record.gender == 'Female':
                                    plan_subcity.registered_female += 1
                                    plan_subcity.total_registered += 1 

                                for field in plan_subcity.field_based_planning:
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
                        if not record.wereda_id.bypass_plannig:
                            plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('wereda_id', '=', record.wereda_id.id)])
                            wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                            if plan_woreda:
                                if record.gender == 'Male':
                                    plan_woreda.registered_male += 1
                                    plan_woreda.total_registered += 1
                                if record.gender == 'Female':
                                    plan_woreda.registered_female += 1
                                    plan_woreda.total_registered += 1

                                for field in plan_woreda.field_based_planning:
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
                else:
                    raise UserError(_("Please Create an Active Budget Year With Approprite Dates!"))

            # CHANGING CURRENT SUPPORTER 
            record.state = 'approved'
            record.candidate_id = candidate.id
            record.cell_id.supporter_ids = [(3, int(record.id))]

            # ADDING CANDIDATE INTO CELL
            all_candidate = record.cell_id.candidate_ids.ids + [candidate.id]
            record.cell_id.candidate_ids = [(5, 0, 0)]
            record.cell_id.candidate_ids = [(6, 0, all_candidate)]

            # EMAIL, NOTIFICATION BEING SENT FOR CONFIRMATION
            mail_temp = self.env.ref('member_registration.supporter_approval')
            mail_temp.send_mail(record.id)
            self.deactivate_activity(record)
            user = self.env.user
            message = _("Congratulations!\n Candidate has been Created.")
            title = _("<h4>Candidate Created!</h4>")
            user.notify_success(message, title, True)  