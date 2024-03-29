# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class CategoryDiscipline(models.Model):
    _name = 'discipline.category'
    _description = 'Reason Category'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']



    # Discipline Categories

    code = fields.Char(string="Code", required=True, translate=True, help="Category code")
    name = fields.Char(string="Name", required=True, translate=True, help="Category name")
    description = fields.Text(string="Details", help="Details for this category", translate=True)
    action_category = fields.Many2one('discipline.action', string="Discipline Action", required=True)


class CategoryDisciplineAction(models.Model):
    _name = 'discipline.action'
    _description = 'Action Category'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    # Discipline Categories

    code = fields.Char(string="Code", translate=True, required=True, help="Category code")
    name = fields.Char(string="Name", required=True, translate=True, help="Category name")
    description = fields.Text(string="Details", help="Details for this category", translate=True)


class DisciplinaryAction(models.Model):
    _name = 'disciplinary.action'
    _description = "Disciplinary Action"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting Explanation'),
        ('submitted', 'Waiting Action'),
        ('action', 'Action Validated'),
        ('cancel', 'Cancelled'),

    ], default='draft', track_visibility='onchange')

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), translate=True)

    employee_name = fields.Many2one('hr.employee', string='Employee', help="Employee name")
    # employee_user = fields.Many2one('res.users', related="employee_name.user_id", string="Employee User")
    # user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Active User")
    department_name = fields.Many2one('hr.department', string='Department', help="Department name")
    discipline_reason = fields.Many2one('discipline.category', string='Reason', help="Choose a disciplinary reason")
    explanation = fields.Text(string="Explanation by Employee", help='Employee have to give Explanation'
                                                                     'to manager about the violation of discipline', translate=True)
    action = fields.Many2one('discipline.action', string="Action", help="Choose an action for this disciplinary action")
    read_only = fields.Boolean(compute="_get_user", default=True)
    warning_letter = fields.Html(string="Warning Letter")
    suspension_letter = fields.Html(string="Suspension Letter")
    termination_letter = fields.Html(string="Termination Letter")
    warning = fields.Integer(default=False)
    action_details = fields.Text(string="Action Details", help="Give the details for this action", translate=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments",
                                      help="Employee can submit any documents which supports their explanation")
    note = fields.Text(string="Internal Note", translate=True)
    joined_date = fields.Date(string="Joined Date", help="Employee joining date")
    complaint_id = fields.Many2one('employee.complaint', readonly=True)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    attachment_amount = fields.Integer(compute="_count_attachments")



    # check_user = fields.Boolean(string="Check User")

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('disciplinary.action')
        return super(DisciplinaryAction, self).create(vals)


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'draft' or record.state == 'explain' or record.state == 'cancel') and self.env.user.has_group('hr_disciplinary_tracking.group_employee_disciplinary_committee') and (record.employee_name.user_id.id != self.env.user.id) or\
                (record.state == 'draft' or record.state == 'explain' or record.state == 'action' or record.state == 'cancel') and self.env.user.has_group('hr.group_hr_manager') and (record.employee_name.user_id.id != self.env.user.id) or\
                (record.state == 'submitted' or record.state == 'action' or record.state == 'cancel') and self.env.user.has_group('hr.group_user_custom') and not self.env.user.has_group('hr_disciplinary_tracking.group_employee_disciplinary_committee'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def add_attachment(self):
        """This function will add attachments"""
        for record in self:
            wizard = self.env['attachment.wizard'].create({
                'res_id': record.id,
                'res_model': 'disciplinary.action'
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


    # Check the user is a manager or employee
    def _get_user(self):

        if self.env.user.has_group('hr_disciplinary_tracking.group_employee_disciplinary_committee'):
            self.read_only = True
        else:
            self.read_only = False

    @api.onchange('employee_name')
    @api.depends('employee_name')
    def onchange_employee_name(self):

        department = self.env['hr.employee'].search([('name', '=', self.employee_name.name)])
        self.department_name = department.department_id.id

        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason')
    @api.depends('discipline_reason')
    def onchange_reason(self):
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    def assign_function(self):
        for rec in self:
            message = "Disciplinary Action Has Been Sent To You. Please Fill Out Your Explanation."
            model = self.env['ir.model'].search([('model', '=', 'disciplinary.action'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Employee Notification')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Employee Notification",
                'date_deadline': date.today() + relativedelta(weeks=2),
                'user_id': rec.employee_name.user_id.id,
                'res_model_id': model.id,
                'res_id': rec.id,
                'activity_type_id': activity_type.id
            })
            if rec.employee_name.user_id:
                rec.employee_name.user_id.notify_warning(message, '<h4>Employee Explanation</h4>', True)
            else:
                raise UserError(_("This Employee Does Not Have Access to The System."))
            rec.state = 'explain'

    def cancel_function(self):
        for rec in self:
            rec.state = 'cancel'

    def set_to_function(self):
        for rec in self:
            rec.state = 'draft'

    def action_function(self):
        for rec in self:
            if not rec.action:
                raise ValidationError(_('You have to select an Action !!'))

            if self.warning == 1:
                if not rec.warning_letter or rec.warning_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Warning Letter in Action Information !!'))

            elif self.warning == 2:
                if not rec.suspension_letter or rec.suspension_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Suspension Letter in Action Information !!'))

            elif self.warning == 3:
                if not rec.termination_letter or rec.termination_letter == '<p><br></p>':
                    raise ValidationError(_('You have to fill up the Termination Letter in  Action Information !!'))

            elif self.warning == 4:
                self.action_details = "No Action Proceed"

            elif self.warning == 5:
                if not rec.action_details:
                    raise ValidationError(_('You have to fill up the  Action Information !!'))
            complaint = rec.complaint_id
            if complaint.state != 'resolved':
                complaint.write({
                    'action': rec.action,
                    'action_details': rec.action_details,
                    'state': 'resolved'
                })
                self.env.cr.commit()
            rec.state = 'action'


    def explanation_function(self):
        for rec in self:
            if not rec.explanation:
                raise ValidationError(_('You must give an explanation !!'))

        self.write({
            'state': 'submitted'
        })
