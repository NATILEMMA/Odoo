# This function will add complaint to employee and to user
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class EmployeeComplaints(models.Model):
    _name="employee.complaint"
    _description = 'Employee Complaint'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_user(self):
        """This function will get the employee name from user"""
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    subject = fields.Many2one('discipline.category', string="Subject", required=True)
    victim_id = fields.Many2one('hr.employee', default=_default_user, string="Victim")
    mode = fields.Selection(selection=[('by_employee', 'By Employee'), ('by_department', 'By Department'), ('by_company', 'By Company')], required=True)
    employee_offendors_ids = fields.Many2many('hr.employee', string="Employees")
    department_offendors_ids = fields.Many2many('hr.department', string="Departments")
    company_offendors_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    action = fields.Many2one('discipline.action', string="Action")
    action_details = fields.Text(string="Action Details")
    circumstances = fields.Text(string="Circumstances")
    state = fields.Selection(string="Complaint status", selection=[('new', 'New'), ('draft', 'Draft'), ('waiting for approval', 'Waiting For Approval'), ('resolved', 'Resolved')], default='new')
    disciplinary_id = fields.Many2one('disciplinary.action', string="Disciplinary Action")
    complaint_assessor_ids = fields.Many2many('res.users', string="Complaint Assessors")
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)



    @api.model
    def create(self, vals):
        """This function will create a complaint and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.complaint')
        vals['state'] = 'draft'
        return super(EmployeeComplaints, self).create(vals)


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'resolved' and self.env.user.has_group('hr_disciplinary_tracking.group_department_disciplinary_committee')) or\
               (record.state == 'resolved' and self.env.user.has_group('hr_disciplinary_tracking.group_company_disciplinary_committee')) or\
               ((record.state == 'waiting for approval' or record.state == 'resolved') and self.env.user.has_group('hr.group_user_custom')):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def in_progress(self):
        """This function will create a disciplinary action when button is clicked"""
        for complaint in self:
            if complaint.mode == 'by_employee':
                for employee in complaint.employee_offendors_ids:
                    self.disciplinary_id = self.env['disciplinary.action'].sudo().create({
                        'name': self.env['ir.sequence'].next_by_code('disciplinary.action'),
                        'employee_name': employee.id,
                        'department_name': employee.department_id.id,
                        'discipline_reason': complaint.subject.id,
                        'note': complaint.circumstances,
                        'joined_date': complaint.create_date,
                        'state': 'draft',
                        'complaint_id': complaint.id,
                        'action': complaint.subject.action_category.id
                    })

                    if self.disciplinary_id.action.name == 'Written Warning':
                        self.disciplinary_id.warning = 1
                    elif self.disciplinary_id.action.name == 'Suspend the Employee for one Week':
                        self.disciplinary_id.warning = 2
                    elif self.disciplinary_id.action.name == 'Terminate the Employee':
                        self.disciplinary_id.warning = 3
                    elif self.disciplinary_id.action.name == 'No Action':
                        self.disciplinary_id.warning = 4
                    else:
                        self.disciplinary_id.warning = 5

            elif complaint.mode == 'by_department':
                all_assessors = []
                for department in complaint.department_offendors_ids:
                    assessors = department.department_complaint_assessors.ids
                    all_assessors += assessors
                complaint.complaint_assessor_ids = [(6, 0, all_assessors)]

                for committee in all_assessors:
                    message = "Complaint Has Been Made About Your Department. Please Make A Review."
                    model = self.env['ir.model'].search([('model', '=', 'employee.complaint'), ('is_mail_activity', '=', True)])
                    activity_type = self.env['mail.activity.type'].search([('name', '=', 'Committee Notification')], limit=1)
                    activity = self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Complaint",
                        'date_deadline': date.today() + relativedelta(months=2),
                        'user_id': committee,
                        'res_model_id': model.id,
                        'res_id': complaint.id,
                        'activity_type_id': activity_type.id
                    })
                    user = self.env['res.users'].search([('id', '=', committee)])
                    # user.notify_warning(message, '<h4>Complaint</h4>', True)
                   

            elif complaint.mode == 'by_company':
                all_assessors = complaint.company_offendors_id.company_complaint_assessors.ids
                complaint.complaint_assessor_ids = [(6, 0, all_assessors)]

                for committee in all_assessors:
                    message = "Complaint Has Been Made About Your Company. Please Make A Review."
                    model = self.env['ir.model'].search([('model', '=', 'employee.complaint'), ('is_mail_activity', '=', True)])
                    activity_type = self.env['mail.activity.type'].search([('name', '=', 'Committee Notification')], limit=1)
                    activity = self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Complaint",
                        'date_deadline': date.today() + relativedelta(months=2),
                        'user_id': committee,
                        'res_model_id': model.id,
                        'res_id': complaint.id,
                        'activity_type_id': activity_type.id
                    })
                    user = self.env['res.users'].search([('id', '=', committee)])
                    # user.notify_warning(message, '<h4>Complaint</h4>', True)

            complaint.state = 'waiting for approval'

    def complaint_reviewed(self):
        """This function will change status after department reviewer is done"""
        for record in self:
            if not record.action:
                raise UserError(_('Please Fill In The Action To Be Taken And Detail Explanation'))
            elif not record.action_details:
                raise UserError(_('Please Fill In The Action To Be Taken And Detail Explanation'))
            record.state ='resolved'

class ResUsersComplaint(models.Model):
    _inherit = "hr.employee"

    employee_complaint_ids = fields.One2many('employee.complaint', 'victim_id')
    discipline_count = fields.Integer(compute="_compute_discipline_count")
    complaint_counter = fields.Integer(compute="_compute_complaint_count")

    def _compute_discipline_count(self):
        """This function will count the number of actions for a user"""
        for record in self:
            actions = self.env['disciplinary.action'].search([('state', 'in', ('explain','action')), ('employee_name', '=', record.id)])
            record.discipline_count = len(actions)

    def _compute_complaint_count(self):
        """This function will compute the number of complaints"""
        for record in self:
            complaints = self.env['employee.complaint'].search([('victim_id', '=', record.id)])
            record.complaint_counter = len(complaints)


class ResUsersComplaint(models.Model):
    _inherit = "hr.employee.public"

    employee_complaint_ids = fields.One2many('employee.complaint', 'victim_id')
    discipline_count = fields.Integer(compute="_compute_discipline_count")
    complaint_counter = fields.Integer(compute="_compute_complaint_count")

    def _compute_discipline_count(self):
        """This function will count the number of actions for a user"""
        for record in self:
            actions = self.env['disciplinary.action'].search([('state', 'in', ('explain','action')), ('employee_name', '=', record.id)])
            record.discipline_count = len(actions)

    def _compute_complaint_count(self):
        """This function will compute the number of complaints"""
        for record in self:
            complaints = self.env['employee.complaint'].search([('victim_id', '=', record.id)])
            record.complaint_counter = len(complaints)


class ResUsersComplaint(models.Model):
    _inherit = "res.users"

    employee_complaint_ids = fields.One2many('employee.complaint', 'victim_id')
    discipline_count = fields.Integer(compute="_compute_discipline_count")
    complaint_counter = fields.Integer(compute="_compute_complaint_count")


    def _compute_discipline_count(self):
        """This function will count the number of actions for a user"""
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', record.id)])
            actions = self.env['disciplinary.action'].search([('state', 'in', ('explain','action')), ('employee_name', '=', employee.id)])
            record.discipline_count = len(actions)


    def _compute_complaint_count(self):
        """This function will compute the number of complaints"""
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', record.id)])
            complaints = self.env['employee.complaint'].search([('victim_id', '=', employee.id)])
            record.complaint_counter = len(complaints)

class HrDepartmentComplaint(models.Model):
    _inherit = "hr.department"

    department_complaint_assessors = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("hr_disciplinary_tracking.group_department_disciplinary_committee").id)], string="Complaint Assessors")

class Company(models.Model):
    _inherit = "res.company"


    company_complaint_assessors = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("hr_disciplinary_tracking.group_company_disciplinary_committee").id)], string="Complaint Assessors") 
