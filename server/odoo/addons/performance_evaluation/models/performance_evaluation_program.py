# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import date

#Personal Competencies
#Workplace Competencies
#Workplace Competencies
#Technical Competencies
#Other Competencies
#Unsatisfactory
#Needs improvements
#Meet Expectation
#Exceed Expectation
#Outstanding
RATING_VALUATION = {
                    '0':'unsatisfactory',
                    '1':'unsatisfactory',
                    '2':'needs_improvements',
                    '3':'meet_expectation',
                    '4':'exceed_expectation',
                    '5':'outstanding'
}
    
class PerformancePeriod(models.Model):
    _name = "performance.period"
    _description = 'Performance Period'
    
    evaluate_before = fields.Integer(required=True)
    
    @api.model
    def create(self, vals):
        """This function will make sure there is only one probation period given"""
        period = self.env['performance.period'].sudo().search([])
        if period:
            raise ValidationError(_("You can only have one Probation Period"))
        return super(PerformancePeriod, self).create(vals)

class PerformanceEvaluationProgramConfig(models.Model):
    _name = 'performance.evaluation.program.config'
    _description = 'Performance Evaluation Program Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name desc"
            
    name = fields.Char(string="Reference", copy=False, translate=True)
    
    personal_section = fields.Boolean()
    workplace_section = fields.Boolean()
    workplace_tw_section = fields.Boolean()
    technical_section = fields.Boolean()
    other_section = fields.Boolean()
    
    performance_evaluator = fields.Selection([
                                    ('csuite', 'C-Suite'),
                                    ('manager', 'Manager'),
                                    ('colleague', 'Colleague'),
                                    ('own', 'Own')
                                ])
    email_notify_user_ids = fields.Many2many("res.users", string='Notify Users if New Evaluation Submited and Confirmed')
    
    hr_email_notify = fields.Boolean("Send Email if HR APPROVE or REJECT Evaluation")
    
    company_id = fields.Many2one("res.company", index=True, default=lambda self: self.env.company)
    evaluation_points_ids = fields.One2many('evaluation.points', 'config_id')
    # personal_line_ids = fields.One2many("perosnal.line", "config_id", string="Personal Competencies", copy=True, auto_join=True, tracking=1)
    # workplace_line_ids = fields.One2many("workplace.line", "config_id", string="Workplace Competencies", copy=True, auto_join=True, tracking=1)
    # workplace_tw_line_ids = fields.One2many("workplace.tw.line", "config_id", string="Other Workplace Competencies", copy=True, auto_join=True, tracking=1)
    # technical_line_ids = fields.One2many("technical.line", "config_id", string="Technical Competencies", copy=True, auto_join=True, tracking=1)
    # other_line_ids = fields.One2many("other.line", "config_id", string="Other Competencies", copy=True, auto_join=True, tracking=1)
    
class Descriptions(models.Model):
    _name="title.description"
    _description="This will describe the subtitle of the evaluation point"

    name = fields.Char(translate=True, required=True)
    evaluation_point = fields.Many2one('evaluation.points')

class EvaluationPoints(models.Model):
    _name="evaluation.points.program"
    _description="This will create evaluation points, their description and their points"

    name = fields.Char(translate=True, required=True)
    # description_ids = fields.One2many('title.description', 'evaluation_point')
    # config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    state = fields.Selection(related="program_id.state")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False, required=True)
    display_type = fields.Selection(
        selection=[
            ('line_point', "Point"),
            ('line_note', "Note"),
        ],
        default="line_point")

    @api.onchange('rating_star')
    def _onchange_rating_star(self):
        for rec in self:
            if not rec.program_id.template_id.performance_evaluator =='own' and rec.program_id.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            if rec.rating_star:
                rec.rating_value = RATING_VALUATION[rec.rating_star]
                rec.rating = rec.rating_star
            else:
                rec.rating_value = False
                rec.rating = False


class EvaluationPoints(models.Model):
    _name="evaluation.points"
    _description="This will create evaluation points, their description and their points"

    name = fields.Char(translate=True, required=True)
    # description_ids = fields.One2many('title.description', 'evaluation_point')
    config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    # program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    # state = fields.Selection(related="program_id.state")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)
    display_type = fields.Selection(
        selection=[
            ('line_point', "Point"),
            ('line_note', "Note"),
        ],
        default="line_point")


class PerosnalLine(models.Model):
    _name = "perosnal.line"
    _description = 'Perosnal Line'
    
    config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    name = fields.Char(string="Description", copy=False)
class WorkplaceLine(models.Model):
    _name = "workplace.line"
    _description = 'Workplace Line'
    
    config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    name = fields.Char(string="Description", copy=False)
class WorkplaceTwLine(models.Model):
    _name = "workplace.tw.line"
    _description = 'Workplace Tw Line'
    
    config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    name = fields.Char(string="Description", copy=False)
class TechnicalLine(models.Model):
    _name = "technical.line"
    _description = 'Technical Line'
    
    config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    name = fields.Char(string="Description", copy=False)
class OtherLine(models.Model):
    _name = "other.line"
    _description = 'Other Line'
    
    config_id = fields.Many2one("performance.evaluation.program.config", ondelete='cascade', index=True, copy=False)
    name = fields.Char(string="Description", copy=False)



class PerformanceEvaluationProgram(models.Model):
    _name = 'performance.evaluation.program'
    _description = 'Performance Evaluation Program'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = "name desc"


    @api.onchange('template_id')
    def _onchange_rating(self):
        for rec in self:
            if rec.template_id:
                total = 0
                rec.evaluation_point_ids = [(5, 0, 0)]
                for point in rec.template_id.evaluation_points_ids:
                    if point.display_type == 'line_point':
                        total += 1
                    pointline = {
                        'name': point.name,
                        'display_type': point.display_type
                    }
                    rec.evaluation_point_ids = [
                        (
                            0,
                            0,
                            pointline
                        )
                    ]
                rec.total_points = total

            #     for pl in rec.template_id.workplace_line_ids:
            #         pline = {
            #                     'name':pl.name
            #                  }
            #         rec.workplace_ev_line_ids = [(0,0,pline)]


            #     for pl in rec.template_id.workplace_tw_line_ids:
            #         pline = {
            #                     'name':pl.name
            #                  }
            #         rec.workplace_tw_ev_line_ids = [(0,0,pline)]
                
            #     for pl in rec.template_id.technical_line_ids:
            #         pline = {
            #                     'name':pl.name
            #                  }
            #         rec.technical_ev_line_ids = [(0,0,pline)]

            #     for pl in rec.template_id.other_line_ids:
            #         pline = {
            #                     'name':pl.name
            #                  }
            #         rec.other_ev_line_ids = [(0,0,pline)]
                        
            else:
                rec.evaluation_point_ids = False
                # rec.workplace_ev_line_ids = False
                # rec.workplace_tw_ev_line_ids = False
                # rec.technical_ev_line_ids = False
                # rec.other_ev_line_ids = False

            rec.evaluator_relationship = rec.template_id.performance_evaluator

            if rec.template_id.performance_evaluator =='manager':
                rec.evaluator_employee_id = rec.employee_id.parent_id
            elif rec.template_id.performance_evaluator =='own':
                rec.evaluator_employee_id = rec.employee_id
            else:
                rec.evaluator_employee_id = False

    @api.onchange('evaluator_employee_id')
    def _compute_evaluator_emp_info(self):
        for rec in self:
            rec.evaluator_department_id = rec.evaluator_employee_id.department_id
            rec.evaluator_job_id = rec.evaluator_employee_id.job_id
            if rec.evaluator_employee_id:
                if rec.evaluator_department_id.id == rec.department_id.id:
                    rec.evaluator_department_relationship = 'intra'
                else:
                    rec.evaluator_department_relationship = 'inter'
            else:
                rec.evaluator_department_relationship = False
            
            
    @api.depends('employee_id')
    def _compute_emp_info(self):
        for rec in self:
            if rec.employee_id.contract_id.state == 'probation':
                rec.on_trial = True
            rec.department_id = rec.employee_id.department_id
            rec.job_id = rec.employee_id.job_id
            rec.manager_id = rec.employee_id.parent_id
            rec.birthday = rec.employee_id.birthday
            rec.country_id = rec.employee_id.country_id
            rec.image_1920 = rec.employee_id.image_1920
            rec.visa_expire = rec.employee_id.visa_expire
            #rec.template_id = False
            #rec.performance_period_id = False
    
    # @api.depends('overall_personal_score','overall_workplace_score','overall_workplace_tw_score','overall_technical_score','overall_other_score')
    # def _compute_overall(self):
    #     for rec in self:
            
    #         rec.overall_score = 0.00
    #         overall_score = 0.00
    #         len_av = 0
    #         if rec.template_id.personal_section:
    #             len_av += 1
    #             overall_score += rec.overall_personal_score
    #         if rec.template_id.workplace_section:
    #             len_av += 1
    #             overall_score += rec.overall_workplace_score
    #         if rec.template_id.workplace_tw_section:
    #             len_av += 1
    #             overall_score += rec.overall_workplace_tw_score
    #         if rec.template_id.technical_section:
    #             len_av += 1
    #             overall_score += rec.overall_technical_score
    #         if rec.template_id.other_section:
    #             len_av += 1
    #             overall_score += rec.overall_other_score
            
    #         if len_av >0:
    #             rec.overall_score =  float(format(overall_score/len_av, '.2f'))
    #         else:
    #             rec.overall_score =  float(format(overall_score/1, '.2f'))

            
    #         if rec.overall_score >= 0 and rec.overall_score<=5:
    #             rec.overall_rating = str(round(rec.overall_score))
    #             rec.overall_rating_value = RATING_VALUATION[rec.overall_rating]
    #             rec.overall_rating_star = rec.overall_rating
    #         else:
    #             rec.overall_rating = False
    #             rec.overall_rating_value = False
    #             rec.overall_rating_star = False


    # @api.depends('evaluation_point_ids.rating_star')
    # def _compute_evaluation_rating(self):
    #     for rec in self:
    #         rec.overall_evaluation_score = 0.00
    #         t_rating = 0.00
    #         for line in rec.evaluation_point_ids:
    #             t_rating += int(line.rating_star)
    #         rec.overall_evaluation_score = float(format(t_rating/rec.total_points, '.2f'))

    # @api.depends('workplace_ev_line_ids.rating')
    # def _compute_workplace_ev(self):
    #     for rec in self:
    #         rec.overall_workplace_score = 0.00
    #         len_ev = len(rec.workplace_ev_line_ids) or 1
    #         t_rating = 0.00
    #         for line in rec.workplace_ev_line_ids:
    #             t_rating += int(line.rating)
    #         rec.overall_workplace_score = float(format(t_rating/len_ev, '.2f'))

    # @api.depends('workplace_tw_ev_line_ids.rating')
    # def _compute_workplace_tw_ev(self):
    #     for rec in self:
    #         rec.overall_workplace_tw_score = 0.00
    #         len_ev = len(rec.workplace_tw_ev_line_ids) or 1
    #         t_rating = 0.00
    #         for line in rec.workplace_tw_ev_line_ids:
    #             t_rating += int(line.rating)
    #         rec.overall_workplace_tw_score = float(format(t_rating/len_ev, '.2f'))

    # @api.depends('technical_ev_line_ids.rating')
    # def _compute_technical_ev(self):
    #     for rec in self:
    #         rec.overall_technical_score = 0.00
    #         len_ev = len(rec.technical_ev_line_ids) or 1
    #         t_rating = 0.00
    #         for line in rec.technical_ev_line_ids:
    #             t_rating += int(line.rating)
    #         rec.overall_technical_score = float(format(t_rating/len_ev, '.2f'))

    # @api.depends('other_ev_line_ids.rating')
    # def _compute_other_ev(self):
    #     for rec in self:
    #         rec.overall_other_score = 0.00
    #         len_ev = len(rec.other_ev_line_ids) or 1
    #         t_rating = 0.00
    #         for line in rec.other_ev_line_ids:
    #             t_rating += int(line.rating)
    #         rec.overall_other_score = float(format(t_rating/len_ev, '.2f'))

    name = fields.Char(string="Reference", copy=False, default=lambda self: _('New'))
    template_id = fields.Many2one("performance.evaluation.program.config", tracking=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('employee_evaluation', 'Employee Remark'),
        ('hr_evaluation', 'HR Evaluation'),
        ('done', 'Completed'),
        ('reject', 'Rejected')
        ], string='Status', copy=False, tracking=1, default='draft')
    
    note = fields.Char(string="Remark", copy=False)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    # personal_ev_line_ids = fields.One2many("program.perosnal.line", "program_id", string="Personal Competencies", copy=True, auto_join=True, tracking=1)

    # workplace_ev_line_ids = fields.One2many("program.workplace.line", "program_id", string="Workplace Competencies", copy=True, auto_join=True, tracking=1)
    # workplace_tw_ev_line_ids = fields.One2many("program.workplace.tw.line", "program_id", string="Other Workplace Competencies", copy=True, auto_join=True, tracking=1)
    # technical_ev_line_ids = fields.One2many("program.technical.line", "program_id", string="Technical Competencies", copy=True, auto_join=True, tracking=1)
    # other_ev_line_ids = fields.One2many("program.other.line", "program_id", string="Other Competencies", copy=True, auto_join=True, tracking=1)
    
    
    active = fields.Boolean(default=True, tracking=1)
    company_id = fields.Many2one("res.company", index=True, default=lambda self: self.env.company)
    performance_period_id = fields.Many2one("performance.period")

    year = fields.Many2one("fiscal.year", string='Year', store=True, track_visibility='onchange', required=True)
    date_from = fields.Date()
    date_to = fields.Date()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    employee_id = fields.Many2one("hr.employee", domain="[('parent_id.user_id', '=', user_id)]", tracking=1, copy=False)
    department_id = fields.Many2one("hr.department", compute="_compute_emp_info", store=True)
    job_id = fields.Many2one("hr.job", compute="_compute_emp_info", store=True)
    
    
    evaluator_employee_id = fields.Many2one("hr.employee", tracking=1, copy=False)
    evaluator_department_id = fields.Many2one("hr.department", compute="_compute_evaluator_emp_info", store=True)
    evaluator_job_id = fields.Many2one("hr.job", compute="_compute_evaluator_emp_info", store=True)
    
    evaluator_department_relationship = fields.Selection([
                                                ('intra', 'Intra Department'),
                                                ('inter', 'Inter Department'),
                                            ], compute="_compute_evaluator_emp_info", store=True)
    evaluator_relationship = fields.Selection([
                                                ('csuite', 'C-Suite'),
                                                ('manager', 'Manager'),
                                                ('colleague', 'Colleague'),
                                                ('own', 'OWN')
                                            ])
    
    manager_id = fields.Many2one("hr.employee", compute="_compute_emp_info", store=True)
    # visa_expire = fields.Date('Visa Expire Date', compute="_compute_emp_info", store=True)
    evaluation_point_ids = fields.One2many('evaluation.points.program', 'program_id')
    on_trial = fields.Boolean(default=False)
    total_points = fields.Integer(store=True)
    image_1920 = fields.Image(compute="_compute_emp_info", store=True)
    # country_id = fields.Many2one(
    #     'res.country', 'Nationality (Country)', compute="_compute_emp_info", store=True)
    # birthday = fields.Date('Date of Birth', compute="_compute_emp_info", store=True)
    date_of_joining = fields.Date(copy=False)
    length_of_service = fields.Char(copy=False)
    # location = fields.Char(copy=False)
    # job_category = fields.Char(copy=False)
    
    disciplinary_action = fields.Char(copy=False)
    nature_of_disclipinary_action = fields.Char(copy=False)
    # annual_leave_balance = fields.Char(copy=False)
    # annual_leave_consumed_this_year = fields.Char(copy=False)
    # visa_days_to_expire = fields.Char(copy=False)
    # labor_card_expiry = fields.Date(copy=False)
    # labor_card_days_to_expire = fields.Char(copy=False)
    
    job_description = fields.Text(copy=False)
    hr_remarks = fields.Text(copy=False)
    manager_remarks = fields.Text(copy=False, translate=True)
    employee_remarks = fields.Text(copy=False, translate=True)
    needs_more_training = fields.Boolean(default=False)
    needs_to_improve = fields.Boolean(default=False)
    try_with_another_job = fields.Boolean(default=False)
    lack_of_required_skills = fields.Boolean(default=False)
    others = fields.Boolean(default=False)
    keep = fields.Boolean(default=False)
    # positive_points = fields.Text(tracking=1, copy=False)
    # negative_points = fields.Text(tracking=1, copy=False)
    extra_remarks = fields.Text(tracking=1, copy=False)
    

    date_of_evaluation = fields.Datetime(copy=False)
    
    overall_score = fields.Float(store=True, tracking=1)
    
    overall_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    overall_rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False, tracking=1)
    overall_rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)
    


    overall_evaluation_score = fields.Float(compute="_compute_evaluation_rating", store=True)
    # overall_workplace_score = fields.Float(compute="_compute_workplace_ev", store=True)
    # overall_workplace_tw_score = fields.Float(compute="_compute_workplace_tw_ev", store=True)
    # overall_technical_score = fields.Float(compute="_compute_technical_ev", store=True)
    # overall_other_score = fields.Float(compute="_compute_other_ev", store=True)
                    


    #Human Resource Remarks for renewal of labor contract
    #Line Manager Remarks for renewal of labor contract



    @api.model
    def create(self, vals):
        # if 'company_id' in vals:
        #     self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('performance.evaluation.program') or _('New')
        if 'employee_id' in vals and 'template_id' in vals:
            performance_evaluator = self.env['performance.evaluation.program.config'].sudo().browse(vals['template_id']).performance_evaluator
            if performance_evaluator =='manager':
                vals['evaluator_employee_id'] = self.env['hr.employee'].sudo().browse(vals['employee_id']).parent_id.id
            elif performance_evaluator =='own':
                vals['evaluator_employee_id'] = vals['employee_id']
            #else:
            #    vals['evaluator_employee_id'] = False
        result = super(PerformanceEvaluationProgram, self).create(vals)
        return result
    

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state == 'done' or record.state == 'reject' or\
             (self.env.user.has_group('performance_evaluation.group_performance_evaluation_program_user') and record.state == 'hr_evaluation') or\
             (self.env.user.has_group('performance_evaluation.group_performance_evaluation_manager') and record.state == 'hr_evaluation') or\
             (self.env.user.has_group('performance_evaluation.group_performance_evaluation_manager') and record.state == 'employee_evaluation') or\
             (self.env.user.has_group('performance_evaluation.group_performance_evaluation_admin') and record.state == 'employee_evaluation'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False
    
    def write(self, vals):
    
        if 'template_id' in vals:
            performance_evaluator = self.env['performance.evaluation.program.config'].sudo().browse(vals['template_id']).performance_evaluator
            if performance_evaluator =='manager':
                vals['evaluator_employee_id'] = self.employee_id.parent_id.id
            elif performance_evaluator =='own':
                vals['evaluator_employee_id'] = self.employee_id.id
            #else:
            #    vals['evaluator_employee_id'] = False
        if 'hr_remarks' in vals and not self.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Update HR Remarks !")
        if 'disciplinary_action' in vals and not self.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Update disciplinary action !")
        if 'nature_of_disclipinary_action' in vals and not self.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Update nature of disclipinary action !")
        res = super(PerformanceEvaluationProgram, self).write(vals)
        return res

    @api.onchange('year')
    def _find_period_of_evaluation(self):
        """This function will create a date_from and date_to from fiscal year"""
        for record in self:
            if record.year:
                record.date_from = record.year.date_from
                record.date_to = record.year.date_to


    def confirm_program(self):
        for rec in self:
            rec.overall_evaluation_score = 0.00
            t_rating = 0.00
            for line in rec.evaluation_point_ids:
                if int(line.rating_star) == 0 and line.display_type == 'line_point':
                   raise ValidationError(_("You Can Not Give Employees a Lower Score Than 1."))
                else:
                    t_rating += int(line.rating_star)
            rec.overall_evaluation_score = float(format(t_rating/rec.total_points, '.2f'))
            # if rec.overall_evaluation_score == 0.00:
            #     raise ValidationError(_("You Can Not Give Employee's a Lower Score Than 1."))
            rec.overall_score = rec.overall_evaluation_score
            rec.overall_rating_star = str(round(rec.overall_score))
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            link = web_base_url + '/web#id=%d&view_type=form&model=%s' % (rec.id, rec._name)
            mail_content = "  Hello  " + \
                    ",<br>New Employee Evaluation Request " + rec.name + ", is added in the system." + \
                    "<br><b>For Employee - </b>" + str(rec.employee_id.name) +\
                    "<br>"+\
                    "<p style='box-sizing:border-box;margin-bottom: 0px;'>" +\
                    "To access Evaluation Request, you can use the following link: </p>" +\
                    "<p style='margin:0px 0 12px 0;box-sizing:border-box;'></p>" +\
                    "<div style='margin: 16px 0px 16px 0px;'>" +\
                    "<a href="+link+ " style='padding: 5px 10px; color: #FFFFFF;"+\
                    "background-color: #875A7B;"+\
                    "border: 1px solid #875A7B;"+\
                    "border-radius: 3px'>"+\
                    "<strong style='box-sizing:border-box;font-weight:bolder;'>View Evaluation Request</strong>" +\
                    "</a>"+\
                    "</div>" +\
                    "<br><br>Thank You, <br>" + str(rec.company_id.name)
        
            main_content = {
                'subject': _('New Employee Evaluation Request - %s for Employee %s') % (rec.name,rec.employee_id.name),
                'author_id': rec.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': rec.evaluator_employee_id.user_id.login,
                'recipient_ids': [(6,0,[user.partner_id.id for user in rec.template_id.email_notify_user_ids])],
            }
            self.env['mail.mail'].create(main_content).sudo().send()
            
            rec.state = 'in_progress'
    
    def submit_evaluation_program(self):
        for rec in self:
            if not rec.template_id.performance_evaluator =='own' and rec.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            model = self.env['ir.model'].search([('model', '=', 'performance.evaluation.program'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Employee Remark')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': "Employee Remark",
                'summary': "Employee Remark",
                'date_deadline': date.today() + relativedelta(weeks=2),
                'user_id': rec.employee_id.user_id.id,
                'res_model_id': model.id,
                'res_id': rec.id,
                'activity_type_id': activity_type.id
            })
            rec.state = 'employee_evaluation'

    def send_evaluation(self):
        """This function will send evaluation to employee"""
        for rec in self:
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            link = web_base_url + '/web#id=%d&view_type=form&model=%s' % (rec.id, rec._name)
            mail_content = "  Hello  " + \
                    ",<br>Employee Evaluation Request " + rec.name + ", is Submitted in the system." + \
                    "<br><b>For Employee - </b>" + str(rec.employee_id.name) +\
                    "<br>"+\
                    "<b>Thank you for your evaluation. </b>" + \
                    "<br>"+\
                    "<p style='box-sizing:border-box;margin-bottom: 0px;'>" +\
                    "To access Evaluation Request, you can use the following link: </p>" +\
                    "<p style='margin:0px 0 12px 0;box-sizing:border-box;'></p>" +\
                    "<div style='margin: 16px 0px 16px 0px;'>" +\
                    "<a href="+link+ " style='padding: 5px 10px; color: #FFFFFF;"+\
                    "background-color: #875A7B;"+\
                    "border: 1px solid #875A7B;"+\
                    "border-radius: 3px'>"+\
                    "<strong style='box-sizing:border-box;font-weight:bolder;'>View Evaluation Request</strong>" +\
                    "</a>"+\
                    "</div>" +\
                    "<br><br>Thank You, <br>" + str(rec.company_id.name)
        
            main_content = {
                'subject': _('Employee Evaluation - %s for Employee %s') % (rec.name,rec.employee_id.name),
                'author_id': rec.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': rec.evaluator_employee_id.user_id.login,
            }
            self.env['mail.mail'].sudo().create(main_content).send()
            
            mail_content1 = "  Hello  " + \
                    ",<br>Employee Evaluation Request " + rec.name + ", is Submitted in the system." + \
                    "<br><b>For Employee - </b>" + str(rec.employee_id.name) +\
                    "<br>"+\
                    "<b>Evaluator Employee - </b>" + str(rec.evaluator_employee_id.name) +\
                    "<br>"+\
                    "<p style='box-sizing:border-box;margin-bottom: 0px;'>" +\
                    "To access Evaluation Request, you can use the following link: </p>" +\
                    "<p style='margin:0px 0 12px 0;box-sizing:border-box;'></p>" +\
                    "<div style='margin: 16px 0px 16px 0px;'>" +\
                    "<a href="+link+ " style='padding: 5px 10px; color: #FFFFFF;"+\
                    "background-color: #875A7B;"+\
                    "border: 1px solid #875A7B;"+\
                    "border-radius: 3px'>"+\
                    "<strong style='box-sizing:border-box;font-weight:bolder;'>View Evaluation Request</strong>" +\
                    "</a>"+\
                    "</div>" +\
                    "<br><br>Thank You, <br>" + str(rec.company_id.name)
        
            main_content1 = {
                'subject': _('HR Evaluation Request - %s for Employee %s') % (rec.name,rec.employee_id.name),
                'author_id': rec.env.user.partner_id.id,
                'body_html': mail_content1,
                'recipient_ids': [(6,0,[user.partner_id.id for user in rec.template_id.email_notify_user_ids])],
            }
            self.env['mail.mail'].sudo().create(main_content1).send()
            rec.date_of_evaluation = datetime.datetime.now()
            rec.state = 'hr_evaluation'

    def approve_hr_program(self):
        for rec in self:
            if rec.template_id.hr_email_notify:
                web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                link = web_base_url + '/web#id=%d&view_type=form&model=%s' % (rec.id, rec._name)
                mail_content = "  Hello  " + \
                        ",<br>Employee Evaluation Request " + rec.name + ", is Completed in the system." + \
                        "<br><b>For Employee - </b>" + str(rec.employee_id.name) +\
                        "<br>"+\
                        "<b>Evaluator Employee - </b>" + str(rec.evaluator_employee_id.name) +\
                        "<br>"+\
                        "<p style='box-sizing:border-box;margin-bottom: 0px;'>" +\
                        "To access Evaluation, you can use the following link: </p>" +\
                        "<p style='margin:0px 0 12px 0;box-sizing:border-box;'></p>" +\
                        "<div style='margin: 16px 0px 16px 0px;'>" +\
                        "<a href="+link+ " style='padding: 5px 10px; color: #FFFFFF;"+\
                        "background-color: #875A7B;"+\
                        "border: 1px solid #875A7B;"+\
                        "border-radius: 3px'>"+\
                        "<strong style='box-sizing:border-box;font-weight:bolder;'>View Evaluation Request</strong>" +\
                        "</a>"+\
                        "</div>" +\
                        "<br><br>Thank You, <br>" + str(rec.company_id.name)
            
                main_content = {
                    'subject': _('HR Evaluation Completed - %s for Employee %s') % (rec.name,rec.employee_id.name),
                    'author_id': rec.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': rec.evaluator_employee_id.user_id.login,
                    'recipient_ids': [(6,0,[user.partner_id.id for user in rec.template_id.email_notify_user_ids])],
                }
                self.env['mail.mail'].sudo().create(main_content).send()
            
            rec.state = 'done'

    def reject_hr_program(self):
        for rec in self:
            if rec.template_id.hr_email_notify:
                web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                link = web_base_url + '/web#id=%d&view_type=form&model=%s' % (rec.id, rec._name)
                mail_content = "  Hello  " + \
                        ",<br>Employee Evaluation Request " + rec.name + ", is Rejected by HR." + \
                        "<br><b>For Employee - </b>" + str(rec.employee_id.name) +\
                        "<br>"+\
                        "<b>Evaluator Employee - </b>" + str(rec.evaluator_employee_id.name) +\
                        "<br>"+\
                        "<p style='box-sizing:border-box;margin-bottom: 0px;'>" +\
                        "To access Evaluation, you can use the following link: </p>" +\
                        "<p style='margin:0px 0 12px 0;box-sizing:border-box;'></p>" +\
                        "<div style='margin: 16px 0px 16px 0px;'>" +\
                        "<a href="+link+ " style='padding: 5px 10px; color: #FFFFFF;"+\
                        "background-color: #875A7B;"+\
                        "border: 1px solid #875A7B;"+\
                        "border-radius: 3px'>"+\
                        "<strong style='box-sizing:border-box;font-weight:bolder;'>View Evaluation Request</strong>" +\
                        "</a>"+\
                        "</div>" +\
                        "<br><br>Thank You, <br>" + str(rec.company_id.name)
            
                main_content = {
                    'subject': _('HR Evaluation Rejected - %s for Employee %s') % (rec.name,rec.employee_id.name),
                    'author_id': rec.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': rec.evaluator_employee_id.user_id.login,
                    'recipient_ids': [(6,0,[user.partner_id.id for user in rec.template_id.email_notify_user_ids])],
                }
                self.env['mail.mail'].sudo().create(main_content).send()
            rec.state = 'reject'
                                 
    def reset_to_draft_program(self):
        for rec in self:
            rec.state = 'draft'


    def send_reminder_email(self):
        for rec in self:
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            link = web_base_url + '/web#id=%d&view_type=form&model=%s' % (rec.id, rec._name)
            mail_content = "  Hello  " + \
                    ",<br>Employee Evaluation Request " + rec.name + ", is pending in the system." + \
                    "<br><b>For Employee - </b>" + str(rec.employee_id.name) +\
                    "<br>"+\
                    "<b>Evaluator Employee - </b>" + str(rec.evaluator_employee_id.name) +\
                    "<br>"+\
                    "<b>Kindly Submit evaluation as early as possible. </b>" + \
                    "<br>"+\
                    "<p style='box-sizing:border-box;margin-bottom: 0px;'>" +\
                    "To access Evaluation Request, you can use the following link: </p>" +\
                    "<p style='margin:0px 0 12px 0;box-sizing:border-box;'></p>" +\
                    "<div style='margin: 16px 0px 16px 0px;'>" +\
                    "<a href="+link+ " style='padding: 5px 10px; color: #FFFFFF;"+\
                    "background-color: #875A7B;"+\
                    "border: 1px solid #875A7B;"+\
                    "border-radius: 3px'>"+\
                    "<strong style='box-sizing:border-box;font-weight:bolder;'>View Evaluation Request</strong>" +\
                    "</a>"+\
                    "</div>" +\
                    "<br><br>Thank You, <br>" + str(rec.company_id.name)
        
            main_content = {
                'subject': _('Reminder for Employee Evaluation - %s for Employee %s') % (rec.name,rec.employee_id.name),
                'author_id': rec.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': rec.evaluator_employee_id.user_id.login,
                'recipient_ids': [(6,0,[user.partner_id.id for user in rec.template_id.email_notify_user_ids])],
            }
            self.env['mail.mail'].sudo().create(main_content).send()
            
            

    def open_all_evaluations(self):
        self.ensure_one()
        records = self.env['performance.evaluation.program'].search([('employee_id', '=', self.employee_id.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("performance_evaluation.performance_evaluation_program_action")
        action["context"] = {
            "create": False,
        }
        if len(records) > 1:
            action['domain'] = [('id', 'in', records.ids)]
        elif len(records) == 1:
            form_view = [(self.env.ref('performance_evaluation.performance_evaluation_program_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = records.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
        
        
class ProgramPerosnalLine(models.Model):
    _name = "program.perosnal.line"
    _description = 'Program Perosnal Line'

    @api.onchange('rating')
    def _onchange_rating(self):
        for rec in self:
            if not rec.program_id.template_id.performance_evaluator =='own' and rec.program_id.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            if rec.rating:
                rec.rating_value = RATING_VALUATION[rec.rating]
                rec.rating_star = rec.rating
            else:
                rec.rating_value = False
                rec.rating_star = False

    program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    state = fields.Selection(related="program_id.state")
    name = fields.Char(string="Description")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)
        
 
            
class ProgramWorkplaceLine(models.Model):
    _name = "program.workplace.line"
    _description = 'Program Workplace Line'

    @api.onchange('rating')
    def _onchange_rating(self):
    
        for rec in self:
            if not rec.program_id.template_id.performance_evaluator =='own' and rec.program_id.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            if rec.rating:
                rec.rating_value = RATING_VALUATION[rec.rating]
                rec.rating_star = rec.rating
            else:
                rec.rating_value = False
                rec.rating_star = False

    program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    state = fields.Selection(related="program_id.state")
    name = fields.Char(string="Description")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)

            
class ProgramWorkplaceTwLine(models.Model):
    _name = "program.workplace.tw.line"
    _description = 'Program workplace tw Line'

    @api.onchange('rating')
    def _onchange_rating(self):
        for rec in self:
            if not rec.program_id.template_id.performance_evaluator =='own' and rec.program_id.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            if rec.rating:
                rec.rating_value = RATING_VALUATION[rec.rating]
                rec.rating_star = rec.rating
            else:
                rec.rating_value = False
                rec.rating_star = False

    program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    state = fields.Selection(related="program_id.state")
    name = fields.Char(string="Description")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)
            
class ProgramTechnicalLine(models.Model):
    _name = "program.technical.line"
    _description = 'Program Technical Line'

    @api.onchange('rating')
    def _onchange_rating(self):
        for rec in self:
            if not rec.program_id.template_id.performance_evaluator =='own' and rec.program_id.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            if rec.rating:
                rec.rating_value = RATING_VALUATION[rec.rating]
                rec.rating_star = rec.rating
            else:
                rec.rating_value = False
                rec.rating_star = False

    program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    state = fields.Selection(related="program_id.state")
    name = fields.Char(string="Description")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)
        
            
class ProgramOtherLine(models.Model):
    _name = "program.other.line"
    _description = 'Program Other Line'

    @api.onchange('rating')
    def _onchange_rating(self):
        for rec in self:
            if not rec.program_id.template_id.performance_evaluator =='own' and rec.program_id.evaluator_employee_id.user_id.id != rec.env.user.id and not rec.env.user.has_group ('performance_evaluation.group_performance_evaluation_admin'):
                raise ValidationError("You are not authorize to Submit Current Evaluation!")
            if rec.rating:
                rec.rating_value = RATING_VALUATION[rec.rating]
                rec.rating_star = rec.rating
            else:
                rec.rating_value = False
                rec.rating_star = False

    program_id = fields.Many2one("performance.evaluation.program", ondelete='cascade', index=True)
    state = fields.Selection(related="program_id.state")
    name = fields.Char(string="Description")
    rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], string='Rating',copy=False)
    rating_value = fields.Selection([
        ('unsatisfactory', 'Unsatisfactory'),
        ('needs_improvements', 'Needs improvements'),
        ('meet_expectation', 'Meet Expectation'),
        ('exceed_expectation', 'Exceed Expectation'),
        ('outstanding', 'Outstanding'),
        ],copy=False)
    rating_star = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], copy=False)
