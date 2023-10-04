"""This file will deal with training for leaders """

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class MembersAssembly(models.Model):
    _name="member.assembly"
    _description="This will handle assemblies for member"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years

    assembly_center = fields.Many2one('res.partner')
    assembly_round = fields.Integer()
    assembly_year = fields.Many2one('fiscal.year', required=True, string='Assembly Year')
    assembly_presence = fields.Selection(selection=[('present', 'Present'), ('absent', 'Absent')], default='absent')
    assembly_participation = fields.Selection(selection=[('voice', 'Voice'), ('non voice', 'None Voice')], default='non voice')
    partner_id = fields.Many2one('res.partner')
    assembly_id = fields.Many2one('assembly')
    meeting_cell_together_id = fields.Many2one('meeting.each.other')
    meeting_cell_with_main_office_id = fields.Many2one('meeting.cells')
    certificate = fields.Boolean(default=True, string="Certificates")

    @api.onchange('assembly_presence')
    def _count_paticipants(self):
        """This function will count the number of participants in assemlby"""
        for record in self:
            if record.assembly_presence == 'present':
                record.assembly_id.participants += 1
                record.meeting_cell_together_id.participant_counter += 1
                record.meeting_cell_with_main_office_id.participant_counter += 1
            if record.assembly_presence == 'absent':
                record.assembly_id.participants -= 1
                record.meeting_cell_together_id.participant_counter -= 1
                record.meeting_cell_with_main_office_id.participant_counter -= 1

    @api.model 
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(MembersAssembly, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'assembly_presence' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_participants = 0
                    for record in lines:
                        if record.assembly_presence == 'present':
                            total_participants += 1
                    line['assembly_presence'] = total_participants
        return res




class Assembly(models.Model):
    _name = 'assembly'
    _description = "This will handle the creation of Assemblies"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']



    def _default_year(self):
        year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if len(year) > 1:
            pass
        else:
            return year.id

    name = fields.Char(string='Reference', required=True, readonly=True, default='New')
    city_id = fields.Many2one('membership.city.handlers', required=True)
    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type", required=True)
    instution_id = fields.Many2one("res.partner", string="Instution",domain= "[('instution_type_id','=',instution_type_id)]", required=True)
    assembly_round = fields.Integer(required=True)
    assembly_year = fields.Many2one('fiscal.year', required=True, string='Assembly Year', readonly=True, default=_default_year)
    start_date = fields.Date()
    end_date = fields.Date()
    member_ids = fields.One2many('member.assembly', 'assembly_id')
    note_id = fields.Text('Description')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    added_members = fields.Boolean(default=False)
    attachment_amount = fields.Integer(compute="_count_attachments")
    participants = fields.Integer()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed'),
        ('print', 'Print'),
    ], string='Status', track_visibility='onchange', default='draft')


    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('assembly')
        # if not vals['start_date'] or not vals['end_date']:
        #     raise UserError(_("Please Add A Start and End Date"))
        return super(Assembly, self).create(vals)


    def unlink(self):
        """This function will delete training in draft state only"""
        for record in self:
            if record.state not in ['draft']:
                raise UserError(_("You Can Only Delete Those Assemblies That Are In 'Draft' State."))
        return super(Assembly, self).unlink()


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
                if record.assembly_year.date_from <= record.start_date and record.start_date > record.assembly_year.date_to:
                    raise UserError(_("The Start Date Picked isn't within the Time Range of the Fiscal Year"))
                if record.assembly_year.date_from > record.start_date:
                    raise UserError(_("The Start Date Picked isn't within the Time Range of the Fiscal Year"))
            if record.end_date:
                if record.assembly_year.date_from <= record.end_date and record.end_date > record.assembly_year.date_to:
                    raise UserError(_("The End Date Picked isn't within the Time Range of the Fiscal Year"))
                if record.assembly_year.date_from > record.end_date:
                    raise UserError(_("The End Date Picked isn't within the Time Range of the Fiscal Year"))
            if record.start_date and record.end_date: 
                if record.end_date < record.start_date:
                    raise UserError(_("Please A Date After The Start Date"))   



    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'print' or record.state == 'cancel' or record.state == 'complete'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    @api.onchange('instution_id')
    def _change_center(self):
        """This function will clear fields"""
        for record in self:
            if not record.instution_type_id and record.instution_id:
                record.instution_type_id = False
                record.instution_id = False


    def _count_attachments(self):
        """This function will count the attchments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0


    def add_members(self):
        """This function will add members"""
        for record in self:
            members = self.env['res.partner'].search(['&', ('member_cells', '!=', False), '|',('is_leader', '=', True), ('is_member', '=', True)])
            if members:
                for memb in members:
                    assembly = self.env['member.assembly'].sudo().create({
                        'assembly_center': record.instution_id.id,
                        'assembly_round': record.assembly_round,
                        'assembly_year': record.assembly_year.id,
                        'partner_id': memb.id,
                        'assembly_id': record.id,
                    })
                record.added_members = True
            else:
                record.added_members = False

    def print_event(self):
        """This function will print out ceritificates"""
        for record in self:
            data = {}
            member_info = []
            for member in record.member_ids:
                if member.assembly_presence == 'present':
                    member_info.append({
                        'name': member.partner_id.name,
                        'program_round': record.assembly_round,
                        'program_convener': record.instution_id.name,
                        'date_from': record.start_date,
                        'date_to': record.end_date,
                        'year': record.assembly_year.name
                    })
            data = {
                'data': member_info
            }
        return self.env.ref('members_features.create_participation_certificate').report_action(self, data=data)


    def complete_event(self):
        """This function will change state"""
        for record in self:
            if len(record.member_ids.ids) == 0:
                raise UserError(_("Please Add Members First"))
            if record.attachment_amount == 0:
                raise UserError(_("Please Attach Attendance Photos Before Finishing Assembly"))
            record.state = 'complete'

    def confirm_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'confirm'

    def cancel_event(self):
        """This function will change state"""
        for record in self:
            if not record.note_id:
                raise UserError(_("Please Add Note To Describe the Reason for Cancelling Assembly"))
            record.state = 'cancel'