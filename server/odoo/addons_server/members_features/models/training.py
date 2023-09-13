"""This file will deal with training for leaders"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Trainings(models.Model):
    _name="leaders.trainings"
    _description="This will handle trainings for leaders"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years

    training_center = fields.Many2one('res.partner')
    training_type = fields.Many2one('training.type', required=True)
    training_round = fields.Integer()
    training_year = fields.Many2one('fiscal.year', required=True, string='Training Year')
    training_result = fields.Selection(selection=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    partner_id = fields.Many2one('res.partner', string="Leader")
    training_id = fields.Many2one('member.training')
    certificate = fields.Boolean(default=True, string="Certificates")

class MemberTraining(models.Model):
    _name = 'member.training'
    _description = "Member Training"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_year(self):
        year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if len(year) > 1:
            pass
        else:
            return year.id

    def _default_wereda(self):
        """This will make the wereda the default wereda for the current user"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This will make the subcity the default subcity for the current user"""
        return self.env['membership.handlers.parent'].search([('parent_manager', '=', self.env.user.id)], limit=1).id

    def _default_city(self):
        """This will make the city the default city for the current user"""
        return self.env['membership.city.handlers'].search([('city_manager', '=', self.env.user.id)], limit=1).id

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
    subcity_id = fields.Many2one('membership.handlers.parent', default=_default_subcity)
    city_id = fields.Many2one('membership.city.handlers', default=_default_city)
    training_type = fields.Many2one('training.type', required=True)
    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type", required=True)
    instution_id = fields.Many2one("res.partner", string="Instution",domain= "[('instution_type_id','=',instution_type_id)]", required=True)
    training_round = fields.Integer(required=True)
    training_year = fields.Many2one('fiscal.year', default=_default_year, required=True, string='Training Year', readonly=True)
    start_date = fields.Date()
    end_date = fields.Date()
    leader_ids = fields.One2many('leaders.trainings', 'training_id')
    note_id = fields.Text('Description')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    added_leaders = fields.Boolean(default=False)
    attachment_amount = fields.Integer(compute="_count_attachments")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed')
    ], string='Status', track_visibility='onchange', default='draft')


    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('member.training')
        if not vals['start_date'] or not vals['end_date']:
            raise UserError(_("Please Add A Start and End Date"))
        return super(MemberTraining, self).create(vals)

    def unlink(self):
        """This function will delete training in draft state only"""
        for record in self:
            if record.state not in ['draft']:
                raise UserError(_("You Can Only Delete Those Trainings That Are In 'Draft' State."))
        return super(MemberTraining, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'cancel' or record.state == 'complete'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    @api.onchange('instution_id')
    def _check_instution_id(self):
        """This funstion will make sure institution type is added first"""
        for record in self:
            if record.instution_id and not record.instution_type_id:
                record.instution_id = False
                raise UserError(_("Please Add Institution Type First"))


    @api.onchange('start_date', 'end_date')
    def _check_start_date(self):
        """This function will check if start date id correct"""
        for record in self:
            if record.start_date:
                if record.start_date < date.today():
                    raise UserError(_("Please A Date After Today"))
                if record.training_year.date_from <= record.start_date and record.start_date > record.training_year.date_to:
                    raise UserError(_("The Start Date Picked isn't within the Time Range of the Fiscal Year"))
                if record.training_year.date_from > record.start_date:
                    raise UserError(_("The Start Date Picked isn't within the Time Range of the Fiscal Year"))
            if record.end_date:
                if record.training_year.date_from <= record.end_date and record.end_date > record.training_year.date_to:
                    raise UserError(_("The End Date Picked isn't within the Time Range of the Fiscal Year"))
                if record.training_year.date_from > record.end_date:
                    raise UserError(_("The End Date Picked isn't within the Time Range of the Fiscal Year"))
            if record.start_date and record.end_date: 
                if record.end_date < record.start_date:
                    raise UserError(_("Please A Date After The Start Date"))   

    def _count_attachments(self):
        """This function will count the attchments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0


    def add_leaders(self):
        """This function will add leaders"""
        for record in self:
            leaders = False
            if not record.wereda_id and not record.subcity_id:
                leaders = self.env['res.partner'].search([('is_leader', '=', True), ('member_cells', '!=', False)])
            elif not record.wereda_id and record.subcity_id:
                leaders = self.env['res.partner'].search([('subcity_id', '=', record.subcity_id.id), ('is_leader', '=', True), ('member_cells', '!=', False)])
            elif record.wereda_id and not record.subcity_id:
                leaders = self.env['res.partner'].search([('wereda_id', '=', record.wereda_id.id), ('is_leader', '=', True), ('member_cells', '!=', False)])
            if leaders:
                for leader in leaders:
                    exists = self.env['leaders.trainings'].search([('partner_id', '=', leader.id), ('training_round', '=', record.training_round), ('training_type', '=', record.training_type.id)])
                    if exists:
                        continue
                    else:
                        trainings = self.env['leaders.trainings'].sudo().create({
                            'training_center': record.instution_id.id,
                            'training_type': record.training_type.id,
                            'training_round': record.training_round,
                            'training_year': record.training_year.id,
                            'partner_id': leader.id,
                            'training_id': record.id,
                        })
                if len(record.leader_ids.ids) == 0:
                    raise UserError(_("Training Can't Be Continued Because All Leaders Have Take Training for this Round and Training Type"))
                else:
                    record.added_leaders = True
            else:
                record.added_leaders = False

    def print_event(self):
        """This function will print out ceritificates"""
        for record in self:
            data = {}
            leader_info = []
            if record.leader_ids:
                for leader in record.leader_ids:
                    leader_info.append({
                        'name': leader.partner_id.name,
                        'program_name': record.training_type.name,
                        'program_round': record.training_round,
                        'program_convener': record.instution_id.name,
                        'date_from': record.start_date,
                        'date_to': record.end_date,
                        'result': leader.training_result,
                        'year': record.training_year.name
                    })
                data = {
                    'data': leader_info
                }
        return self.env.ref('create_training_certificate').report_action(self, data=data)

    def complete_event(self):
        """This function will change state"""
        for record in self:
            if len(record.leader_ids.ids) == 0:
                raise UserError(_("Please Add Leaders First"))
            if record.attachment_amount == 0:
                raise UserError(_("Please Attach Attendance Photos Before Finishing Training"))
            record.state = 'complete'

    def confirm_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'confirm'

    def cancel_event(self):
        """This function will change state"""
        for record in self:
            if not record.note_id:
                raise UserError(_("Please Add Note To Describe the Reason for Cancelling Training"))
            record.state = 'cancel'