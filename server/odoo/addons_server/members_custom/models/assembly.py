"""This file will deal with training for leaders """

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AssemblyPlace(models.Model):
    _name="training.type"
    _description="This will create the training types"

    name = fields.Char(required=True, translate=True)

class MembersAssembly(models.Model):
    _name="member.assembly"
    _description="This will handle assemblies for member"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    assembly_center = fields.Many2one('res.partner')
    assembly_round = fields.Integer()
    assembly_year = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year')
    assembly_presence = fields.Selection(selection=[('present', 'Present'), ('absent', 'Absent')], default='absent')
    assembly_participation = fields.Selection(selection=[('voice', 'Voice'), ('non voice', 'None Voice')], default='non voice')
    partner_id = fields.Many2one('res.partner')
    wereda_id = fields.Many2one('membership.handlers.branch', related="partner_id.wereda_id", store=True)
    main_office_id = fields.Many2one('main.office', related="partner_id.main_office", store=True)
    cell_id = fields.Many2one('member.cells', related="partner_id.member_cells", store=True)
    cell_league_id = fields.Many2one('member.cells', related="partner_id.league_member_cells", store=True)
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


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    city_id = fields.Many2one('membership.city.handlers', required=True)
    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type", required=True)
    instution_id = fields.Many2one("res.partner", string="Instution",domain= "[('instution_type_id','=',instution_type_id)]", required=True)
    assembly_round = fields.Integer(required=True)
    assembly_year = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Assembly Year', required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    member_ids = fields.One2many('member.assembly', 'assembly_id')
    note_id = fields.Text('Description')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    added_members = fields.Boolean(default=False)
    participants = fields.Integer()
    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed'),
        ('print', 'Print'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')


    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('assembly')
        vals['state'] = 'draft'
        if not vals['start_date'] or not vals['end_date']:
            raise UserError(_("Please Add A Start and End Date"))
        return super(Assembly, self).create(vals)

    def unlink(self):
        """This will handle deleting Assembly"""
        for record in self:
            assemblies = self.env['member.assembly'].search([('id', '=', record.id)])
            if assemblies:
                raise UserError(_("You Can Not Delete an Assembly That Has Been Confirmed"))
        return super(Assembly, self).unlink()


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



    def add_members(self):
        """This function will add members"""
        for record in self:
            members = self.env['res.partner'].search(['|', ('is_leader', '=', True), ('is_member', '=', True)])
            print(members)
            if members:
                for memb in members:
                    assembly = self.env['member.assembly'].sudo().create({
                        'assembly_center': record.instution_id.id,
                        'assembly_round': record.assembly_round,
                        'assembly_year': record.assembly_year,
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
                        'year': record.assembly_year
                    })
            data = {
                'data': member_info
            }
        return self.env.ref('members_custom.create_participation_certificate').report_action(self, data=data)


    def complete_event(self):
        """This function will change state"""
        for record in self:
            if len(record.member_ids.ids) == 0:
                raise UserError(_("Please Add Members First"))
            record.state = 'complete'

    def confirm_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'confirm'

    def cancel_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'cancel'