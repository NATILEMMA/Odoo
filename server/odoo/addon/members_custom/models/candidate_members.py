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
    name = fields.Char(required=True, translate=True, track_visibility='onchange')
    age = fields.Integer(required=True)
    date = fields.Date(index=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True)
    ethnic_group = fields.Many2one('ethnic.groups')
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    other_job_trainings = fields.Char(translate=True)
    source_of_livelihood = fields.Selection(selection=[('governmental', 'Governmental'), ('private', 'Private'), ('individual', 'Individual'), ('stay at home', 'Stay At Home')])
    income = fields.Float(store=True)
    work_experience_ids = fields.One2many('work.experience', 'candidate_id')
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
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
    reason = fields.Text(translate=True)
    supporter_id = fields.Many2one('supporter.members', store=True, readonly=True)
    note_id = fields.Text()


    @api.model
    def create(self, vals):
        """This function will compute the becomes_member_on"""
        res = super(CandidateMembers, self).create(vals)
        res.becomes_member_on = res.create_date + relativedelta(months=6)             
        return res


    def send_notification_to_woreda_manager(self):
        """This function will alert a woreda manager for candidate approval"""
        all_candidate = self.env['candidate.members'].search([('becomes_member_on', '=', date.today()), ('state', 'in', ['new', 'postponed'])])
        for candidate in all_candidate:
            wereda_manager = candidate.wereda_id.branch_manager
            candidate.write({'state': 'waiting for approval'})
            message = str(candidate.name) + "'s 6 month is Today. Please make a decision about the state of their membership."
            model = self.env['ir.model'].search([('model', '=', 'candidate.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Candidate Approval')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Approval",
                'date_deadline': date.today() + relativedelta(month=2),
                'user_id': wereda_manager.id,
                'res_model_id': model.id,
                'res_id': candidate.id,
                'activity_type_id': activity_type.id
            })
            wereda_manager.notify_warning(message, '<h4>Candidate Approval</h4>', True)

    def add_attachment(self):
        """This function will add attachments"""
        for record in self:
            wizard = self.env['attachment.wizard'].create({
                'res_id': record.id,
                'res_model': 'candidate.members'
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
        wizard = self.env['archive.candidate.wizard'].create({
            'reason': self.reason
        })
        return {
            'name': _('Archive Members Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.candidate.wizard',
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

    def deny_membership(self):
        """This function will return state to new"""
        for record in self:
            if record.note_id == False:
                raise ValidationError(_("Please Give A Reason In The Note Section As To Why You Want To Deny Membership To This Candidate"))
            else:
                record.state = 'rejected'

    @api.onchange('source_of_livelihood')
    def _remove_data(self):
       """This function will remove data if source_of_livelihood is stay at home"""
       for record in self:
           if record.source_of_livelihood == 'stay at home':
               for jobs in record.work_experience_ids:
                   jobs.current_job = False

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                if len(record.phone) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.phone[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))


    @api.onchange('house_phone_number')
    def _proper_house_phone_number(self):
        """This function will check if house_phone_number is of proper format"""
        for record in self:
            if record.house_phone_number:
                if len(record.house_phone_number) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.house_phone_number[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))

    @api.onchange('office_phone_number')
    def _proper_office_phone_number(self):
        """This function will check if house_phone_number is of proper format"""
        for record in self:
            if record.office_phone_number:
                if len(record.office_phone_number) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.office_phone_number[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'approved' or record.state == 'rejected'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            if self.env.user.has_group('members_custom.member_group_agent'):
                record.x_css = '<style> .o_form_button_create {display:None}</style>'
            else:
                record.x_css = False


    def create_members(self):
        """This function will create members from candidates"""
        for record in self:
            if record.attachment_amount == 0:
                raise ValidationError(_("Please Add An Attachment To Justify Approval."))
            if record.age < 18:
                raise UserError(_("A Candidate Who Is Not 18 Or Above Can't Be A Member"))
            wizard = self.env['create.from.candidate.wizard'].create({
                'candidate_id': record.id
            })
            return {
                'name': _('Create Members From Candidate Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.from.candidate.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }