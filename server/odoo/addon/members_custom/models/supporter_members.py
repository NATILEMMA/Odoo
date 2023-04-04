"""This file will deal with the handling of supporter members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class SupportingMembers(models.Model):
    _name="supporter.members"
    _description="Supporter Approval"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(translate=True, required=True, track_visibility='onchange')
    age = fields.Integer(copy=False, required=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], required=True)
    ethnic_group = fields.Many2one('ethnic.groups')
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
    start_of_support = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Supporter Start Year', required=True)
    attachment_amount = fields.Integer(compute="_count_attachments")
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    state = fields.Selection(selection=[('new', 'New'), ('waiting for approval', 'Waiting For Approval'), ('postponed', 'Postponed'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='new', required=True, track_visibility='onchange')
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    active = fields.Boolean(default=True, track_visibility='onchange')
    reason = fields.Text(translate=True)
    becomes_a_candidate_on = fields.Date(string="Becomes A Candidate On", track_visibility='onchange')
    note_id = fields.Text()


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        if vals['age'] == 0:
            raise UserError(_("Please Add The Appropriate Age Of The Supporter"))
        exists = self.env['supporter.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone'])])
        if exists:
            raise UserError(_("A supporter with the same name, gender and phone already exists, Please make sure it isn't a duplicated data"))
        res = super(SupportingMembers, self).create(vals)
        res.becomes_a_candidate_on = res.create_date + relativedelta(months=3)
        res.state = 'new'
        year = self.env['fiscal.year'].search([('state', '=', 'active')])
        if year.date_from <= res.create_date.date() <= year.date_to:
            plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
            if plan_city:
                if res.gender == 'Male':
                    plan_city.registered_male += 1
                    plan_city.total_registered += 1
                if res.gender == 'Female':
                    plan_city.registered_female += 1
                    plan_city.total_registered += 1
                plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                if plan_city.accomplished <= 50.00:
                    plan_city.colors = 'orange'
                if 50 < plan_city.accomplished < 75:
                    plan_city.colors = 'blue'
                if plan_city.accomplished >= 75:
                    plan_city.colors = 'green'
            plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('subcity_id', '=', res.subcity_id.id)])
            if plan_subcity:
                if res.gender == 'Male':
                    plan_subcity.registered_male += 1
                    plan_subcity.total_registered += 1
                if res.gender == 'Female':
                    plan_subcity.registered_female += 1
                    plan_subcity.total_registered += 1 
                plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
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
            plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('wereda_id', '=', res.wereda_id.id)])
            if plan_woreda:
                if res.gender == 'Male':
                    plan_woreda.registered_male += 1
                    plan_woreda.total_registered += 1
                if res.gender == 'Female':
                    plan_woreda.registered_female += 1
                    plan_woreda.total_registered += 1    
                plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
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
        return res


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

    def add_attachment(self):
        """This function will add attachments"""
        for record in self:
            wizard = self.env['attachment.wizard'].create({
                'res_id': record.id,
                'res_model': 'supporter.members'
            })
            return {
                'name': _('Create Attachment Wizard'),
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
            'reason': self.reason
        })
        return {
            'name': _('Archive Members Wizard'),
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

    def postpone_approval(self):
        """This function will postpone decision"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Justify Postponement."))
            else:
                record.state = 'postponed'

    def deny_candidancy(self):
        """This function will return state to new"""
        for record in self:
            if record.note_id == False:
                raise ValidationError(_("Please Give A Reason In The Note Section As To Why You Want To Deny Candidacy To This Supporter"))
            else:
                record.state = 'rejected'

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
                'education_level': record.education_level.id,
                'field_of_study_id': record.field_of_study_id.id,
                'ethnic_group': record.ethnic_group.id,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'house_number': record.house_number,
                'phone': record.phone,
                'income': record.income,
                'supporter_id': record.id
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
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year.date_from <= date.today() <= year.date_to:
                plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                city_report = self.env['annual.plan.report'].search([('annual_plan_city_id', '=', plan_city.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                if plan_city:
                    if record.gender == 'Male':
                        plan_city.registered_male += 1
                        plan_city.total_registered += 1
                    if record.gender == 'Female':
                        plan_city.registered_female += 1
                        plan_city.total_registered += 1
                    plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                    city_report.registered += 1
                    city_report.accomplished = (city_report.registered / plan_city.total_estimated) * 100
                    if plan_city.accomplished <= 50.00:
                        plan_city.colors = 'orange'
                    if 50 < plan_city.accomplished < 75:
                        plan_city.colors = 'blue'
                    if plan_city.accomplished >= 75:
                        plan_city.colors = 'green'
                plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('subcity_id', '=', record.subcity_id.id)])
                subcity_report = self.env['annual.plan.report'].search([('annual_plan_subcity_id', '=', plan_subcity.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])                
                if plan_subcity:
                    if record.gender == 'Male':
                        plan_subcity.registered_male += 1
                        plan_subcity.total_registered += 1
                    if record.gender == 'Female':
                        plan_subcity.registered_female += 1
                        plan_subcity.total_registered += 1 
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
                plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('wereda_id', '=', record.wereda_id.id)])
                wereda_report = self.env['annual.plan.report'].search([('annual_plan_wereda_id', '=', plan_woreda.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today())])
                if plan_woreda:
                    if record.gender == 'Male':
                        plan_woreda.registered_male += 1
                        plan_woreda.total_registered += 1
                    if record.gender == 'Female':
                        plan_woreda.registered_female += 1
                        plan_woreda.total_registered += 1
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
            record.candidate_id = candidate
            record.state = 'approved'