"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class MeetingCells(models.Model):
    _name = "meeting.cells"

    def _default_main(self):
        active_id = self.env.context.get('active_id')
        return self.env['main.office'].search([('id', '=', active_id)])

    def _default_year(self):
        year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if len(year) > 1:
            pass
        else:
            return year.id

    name = fields.Char(translate=True, readonly=True)
    date_of_meeting = fields.Date()
    place_of_meeting = fields.Char(translate=True, required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    year = fields.Many2one('fiscal.year', default=_default_year, required=True)
    main_id = fields.Many2one('main.office', readonly=True, default=_default_main)
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], related="main_id.for_which_members")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_id)]", string="Cell")
    cell_id_league = fields.Many2one('member.cells', domain="[('main_office_league', '=', main_id)]", string="Cell")
    meeting_minute = fields.Text('Meeting Minute')
    state = fields.Selection(selection=[('new', 'New'), ('pending', 'Pending'), ('started', 'Started'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], default='new')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    next_date_of_meeting = fields.Date()
    participant_counter = fields.Integer()


    @api.model
    def create(self, vals):
        """This will create the naming of the meeting"""
        res = super(MeetingCells, self).create(vals)
        if not res.date_of_meeting:
            raise UserError(_("Please Add Date of Meeting"))
        res.name = "Meeting On " + str(res.date_of_meeting)
        if res.start_time == 0.00 or res.end_time == 0.00:
            raise UserError(_("Please Add Start and End Time of Meeting"))
        res.state = 'pending'
        return res

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'pending' or record.state == 'finished' or record.state == 'cancelled'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def remind_meeting_cells(self):
        """This function will remind meeting"""
        pass

    @api.onchange('date_of_meeting')
    def _change_naming(self):
        """This function will change the naming"""
        for record in self:
            if record.date_of_meeting:
                record.name = "Meeting on " + str(record.date_of_meeting)
                if record.date_of_meeting < date.today():
                    raise UserError(_("Please A Date After Today"))

    @api.onchange('next_date_of_meeting')
    def _change_naming(self):
        """This function will change the naming"""
        for record in self:
            if record.next_date_of_meeting:
                if record.next_date_of_meeting <= record.date_of_meeting:
                    raise UserError(_("Please A Date After The Current Meeting Date"))

    def finished_meeting(self):
        """This function will close a meeting"""
        for record in self:
            if not record.meeting_minute:
                raise UserError(_("Please Add Meeting Minutes"))
            if not record.next_date_of_meeting:
                raise UserError(_("Please Add Next Date of Meeting"))
            record.state = 'finished'

    def cancel_meeting(self):
        """This function will cancel a meeting"""
        for record in self:
            record.state = 'cancelled'

    def start_meeting(self):
        """This function will start a meeting"""
        for record in self:
            if record.cell_id.members_ids:
                for member in record.cell_id.members_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_with_main_office_id': record.id,
                    })
            if record.cell_id.leaders_ids:
                for member in record.cell_id.leaders_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_with_main_office_id': record.id,
                    }) 
            if record.cell_id_league.leagues_ids:
                for member in record.cell_id_league.leagues_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_with_main_office_id': record.id,
                    }) 
            if record.cell_id_league.league_leaders_ids:
                for member in record.cell_id_league.league_leaders_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_with_main_office_id': record.id,
                    })                
            record.state = 'started'


class MeetingEachOther(models.Model):
    _name = "meeting.each.other"

    def _default_cell(self):
        active_id = self.env.context.get('active_id')
        return self.env['member.cells'].search([('id', '=', active_id)])


    def _default_year(self):
        year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if len(year) > 1:
            pass
        else:
            return year.id

    name = fields.Char(translate=True, readonly=True)
    date_of_meeting = fields.Date()
    place_of_meeting = fields.Char(translate=True, required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    year = fields.Many2one('fiscal.year', default=_default_year, required=True)
    cell_id = fields.Many2one('member.cells', readonly=True, default=_default_cell)
    meeting_minute = fields.Text('Meeting Minute')
    state = fields.Selection(selection=[('new', 'New'), ('pending', 'Pending'), ('started', 'Started'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], default='new')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    next_date_of_meeting = fields.Date()
    participant_counter = fields.Integer()


    @api.model
    def create(self, vals):
        """This will create the naming of the meeting"""
        res = super(MeetingEachOther, self).create(vals)
        if not res.date_of_meeting:
            raise UserError(_("Please Add Date of Meeting"))
        if res.start_time == 0.00 or res.end_time == 0.00:
            raise UserError(_("Please Add Start and End Time of Meeting"))
        res.name = "Meeting On " + str(res.date_of_meeting)
        res.state = 'pending'
        return res

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'pending' or record.state == 'finished' or record.state == 'cancelled'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def remind_meeting_each_other(self):
        """This function will remind meeting with main office"""
        pass

    @api.onchange('date_of_meeting')
    def _change_naming(self):
        """This function will change the naming"""
        for record in self:
            if record.date_of_meeting:
                record.name = "Meeting on " + str(record.date_of_meeting)
                if record.date_of_meeting < date.today():
                    raise UserError(_("Please A Date After Today"))


    @api.onchange('next_date_of_meeting')
    def _change_naming(self):
        """This function will change the naming"""
        for record in self:
            if record.next_date_of_meeting:
                if record.next_date_of_meeting <= record.date_of_meeting:
                    raise UserError(_("Please A Date After The Current Meeting Date"))


    def finished_meeting(self):
        """This function will close a meeting"""
        for record in self:
            if not record.meeting_minute:
                raise UserError(_("Please Add Meeting Minutes"))
            if not record.next_date_of_meeting:
                raise UserError(_("Please Add Next Date of Meeting"))
            record.state = 'finished'

    def cancel_meeting(self):
        """This function will cancel a meeting"""
        for record in self:
            record.state = 'cancelled'

    def start_meeting(self):
        """This function will start a meeting"""
        for record in self:
            if record.cell_id.members_ids:
                for member in record.cell_id.members_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_together_id': record.id,
                    })
            if record.cell_id.leaders_ids:
                for member in record.cell_id.leaders_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_together_id': record.id,
                    }) 
            if record.cell_id.leagues_ids:
                for member in record.cell_id.leagues_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_together_id': record.id,
                    }) 
            if record.cell_id.league_leaders_ids:
                for member in record.cell_id.league_leaders_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_together_id': record.id,
                    })                
            record.state = 'started'


class MeetingEachOtherMain(models.Model):
    _name = "meeting.each.other.main"

    def _default_main(self):
        active_id = self.env.context.get('active_id')
        return self.env['main.office'].search([('id', '=', active_id)])


    def _default_year(self):
        year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if len(year) > 1:
            pass
        else:
            return year.id

    name = fields.Char(translate=True, readonly=True)
    date_of_meeting = fields.Date()
    place_of_meeting = fields.Char(translate=True, required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    year = fields.Many2one('fiscal.year', default=_default_year, required=True)
    main_id = fields.Many2one('main.office', readonly=True, default=_default_main)
    meeting_minute = fields.Text('Meeting Minute')
    state = fields.Selection(selection=[('new', 'New'), ('pending', 'Pending'), ('started', 'Started'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], default='new')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    next_date_of_meeting = fields.Date()


    @api.model
    def create(self, vals):
        """This will create the naming of the meeting"""
        res = super(MeetingEachOtherMain, self).create(vals)
        if not res.date_of_meeting:
            raise UserError(_("Please Add Date of Meeting"))
        if res.start_time == 0.00 or res.end_time == 0.00:
            raise UserError(_("Please Add Start and End Time of Meeting"))
        res.name = "Meeting On " + str(res.date_of_meeting)
        res.state = 'pending'
        return res

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'pending' or record.state == 'finished' or record.state == 'cancelled'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def remind_meeting_each_other_main(self):
        """This function will remind meeting with main office eachother"""
        pass

    @api.onchange('date_of_meeting')
    def _change_naming(self):
        """This function will change the naming"""
        for record in self:
            if record.date_of_meeting:
                record.name = "Meeting on " + str(record.date_of_meeting)
                if record.date_of_meeting < date.today():
                    raise UserError(_("Please A Date After Today"))


    @api.onchange('next_date_of_meeting')
    def _change_naming(self):
        """This function will change the naming"""
        for record in self:
            if record.next_date_of_meeting:
                if record.next_date_of_meeting <= record.date_of_meeting:
                    raise UserError(_("Please A Date After The Current Meeting Date"))

    def finished_meeting(self):
        """This function will close a meeting"""
        for record in self:
            if not record.meeting_minute:
                raise UserError(_("Please Add Meeting Minutes"))
            if not record.next_date_of_meeting:
                raise UserError(_("Please Add Next Date of Meeting"))
            record.state = 'finished'

    def cancel_meeting(self):
        """This function will cancel a meeting"""
        for record in self:
            record.state = 'cancelled'

    def start_meeting(self):
        """This function will start a meeting"""
        for record in self:
            record.state = 'started'

class MainOfficeMembersConfiguration(models.Model):
    _name = "cell.configuration"
    _description = "This model will handle the configuration of member amount in main office"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    for_members_or_leagues = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True)
    minimum_number = fields.Integer(required=True, track_visibility='onchange')
    maximum_number = fields.Integer(required=True, track_visibility='onchange')
    reject = fields.Boolean(default=False, track_visibility='onchange')

    @api.model
    def create(self, vals):
        """This will check if there are more than one member/league"""
        exists = self.env['cell.configuration'].search([('for_members_or_leagues', '=', vals['for_members_or_leagues'])])
        if exists:
            raise UserError(_("You Already Have A Configuration For This Type."))
        return super(MainOfficeMembersConfiguration, self).create(vals)


class CellMembersConfiguration(models.Model):
    _name = "main.office.configuration"
    _description = "This model will handle the configuration of member amount in cells"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    for_members_or_leagues = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True)
    maximum_cell = fields.Integer(required=True, track_visibility='onchange')
    reject = fields.Boolean(default=False, track_visibility='onchange')    

    @api.model
    def create(self, vals):
        """This will check if there are more than one member/league"""
        exists = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', vals['for_members_or_leagues'])])
        if exists:
            raise UserError(_("You Already Have A Configuration For This Type."))
        return super(CellMembersConfiguration, self).create(vals)


class MainOffice(models.Model):
    _name="main.office"
    _description="This model will contain the main offices the cells bellong in"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(required=True, translate=True, track_visibility='onchange')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange', string="League or Member")
    member_main_type_id = fields.Many2one('membership.organization', track_visibility='onchange')
    league_main_type_id = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange')
    cell_ids = fields.One2many('member.cells', 'main_office', readonly=True, copy=False, track_visibility='onchange')
    league_cell_ids = fields.One2many('member.cells', 'main_office_league', readonly=True, copy=False, track_visibility='onchange')
    total_cell = fields.Integer(compute="_calculate_cells", store=True)
    total_cell_league = fields.Integer(compute="_calculate_league_cells", store=True)
    total_member_fee = fields.Float(compute="_assign_to_main_office", store=True)
    total_member = fields.Integer(compute="_assign_to_main_office", store=True)
    total_league = fields.Integer(compute="_assign_to_main_office_league", store=True)
    total_league_fee = fields.Float(compute="_assign_to_main_office_league", store=True)
    total_members = fields.Integer(compute="_all_members_main", store=True, track_visibility='onchange')
    total_leagues = fields.Integer(compute="_all_members_main", store=True)
    leader_ids = fields.Many2many('res.partner', 'leader_main_rel', copy=False, readonly=True, domain="['&', '&', '&', '&', ('member_responsibility', '=', 3), ('membership_org','=', member_main_type_id), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", track_visibility='onchange')
    league_leader_ids = fields.Many2many('res.partner', 'league_leader_rel', readonly=True, domain="['&', '&', '&', '&', ('league_org','=', league_main_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False), ('league_responsibility', '=', 3)]", copy=False, track_visibility='onchange')
    total_membership_fee = fields.Float(compute="_all_members_main_office_fee", store=True)
    total_leagues_fee = fields.Float(compute="_all_members_main_office_fee", store=True)
    cells = fields.Boolean(default=False)
    main_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_main_manager").id)], readonly=True, store=True)
    main_finance = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_main_finance").id)], readonly=True, store=True)
    main_assembler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_main_assembler").id)], readonly=True, store=True)
    meeting_memebers_every = fields.Integer() 
    pending_meetings_cells = fields.Integer(compute="_get_total_cell") 
    pending_meetings = fields.Integer(compute="_get_total") 
     
    
    _sql_constraints = [('name_constraint', 'unique(name)', 'name must be unique.'),] 

    @api.model
    def create(self, vals):
        """This function will create main office and confim config is set"""
        res = super(MainOffice, self).create(vals)
        config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', res.for_which_members)])
        if not config:
            raise UserError(_("Please Configure The Number of Cells Allowed In A Single Main Office"))
        return res

    @api.onchange('subcity_id')
    def _change_all_field(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False
                record.member_main_type_id = False
                record.league_main_type_id = False

    @api.onchange('wereda_id')
    def _change_all_field_after_wereda(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.wereda_id :
                record.member_main_type_id = False
                record.league_main_type_id = False

    @api.onchange('for_which_members')
    def _chnage_all_field_after_selection(self):
        """This function will make the organization false"""
        for record in self:
            if record.for_which_members:
                record.member_main_type_id = False
                record.league_main_type_id = False

    @api.onchange('main_admin', 'main_finance', 'main_assembler')
    def _change_admin(self):
        """This function will add cell admin to the leaders"""
        for record in self:
            if record.main_admin:
                if record.main_admin.partner_id.is_league and record.main_admin.partner_id.id not in record.league_leader_ids.ids:
                    raise UserError(_("This Administrator Doesn't Belong In The Listed Cells"))
                if (record.main_admin.partner_id.is_member or record.main_admin.partner_id.is_leader) and record.main_admin.partner_id.id not in record.leader_ids.ids:
                    raise UserError(_("This Administrator Doesn't Belong In The Listed Cells"))
            if record.main_finance:
                if record.main_finance.partner_id.is_league and record.main_finance.partner_id.id not in record.cell_ids.league_cell_ids.ids:
                    raise UserError(_("This Finance Handler Doesn't Belong In The Listed Cells"))
                if (record.main_finance.partner_id.is_member or record.main_finance.partner_id.is_leader) and record.main_finance.partner_id.id not in record.cell_ids.members_ids.ids:
                    raise UserError(_("This Finance Handler Doesn't Belong In The Listed Cells"))
            if record.main_assembler:
                if record.main_assembler.partner_id.is_league and record.main_assembler.partner_id.id not in record.cell_ids.league_cell_ids.ids:
                    raise UserError(_("This Finance Handler Doesn't Belong In The Listed Cells"))
                if (record.main_assembler.partner_id.is_member or record.main_assembler.partner_id.is_leader) and record.main_assembler.partner_id.id not in record.cell_ids.members_ids.ids:
                    raise UserError(_("This Finance Handler Doesn't Belong In The Listed Cells"))


    def unlink(self):
        """This function will check if cell has any cells if not it can be deleted"""
        for record in self:
            if record.cell_ids and len(record.cell_ids) > 0:
                raise UserError(_("You can't Delete This Main Office Because It has Cells In It."))
            if record.league_cell_ids and len(record.league_cell_ids) > 0:
                raise UserError(_("You can't Delete This Main Office Because It has Cells In It."))
            if record.leader_ids and len(record.leader_ids) > 0:
                raise UserError(_("You can't Delete This Main Office Because It has Leaders In It."))
        return super(MainOffice, self).unlink()


    @api.depends('cell_ids.leaders_ids', 'cell_ids.members_ids')
    def _assign_to_main_office(self):
        """This function will assign leaders to total members and total fee"""
        for record in self:
            total = 0.00
            record.total_members = record.total_member = len(record.cell_ids.leaders_ids.ids) + len(record.cell_ids.members_ids.ids)
            if record.cell_ids.leaders_ids:
                for leader in record.cell_ids.leaders_ids:
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            if record.cell_ids.members_ids:
                exists = record.cell_ids.members_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_main_assembler'))
                if len(exists.ids) > 1:
                    raise UserError(_("You Can Only Have One Main Office Assembler"))
                exists_2 = record.cell_ids.members_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_main_finance'))
                if len(exists_2.ids) > 1:
                    raise UserError(_("You Can Only Have One Main Office Assembler"))
                for member in record.cell_ids.members_ids:
                    user = self.env['res.users'].search([('id', '=', member.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_main_finance'):
                        record.main_finance = user.id
                    if user.has_group('members_custom.member_group_main_assembler'):
                        record.main_assembler = user.id
                    total += (member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent)
            record.total_membership_fee = record.total_member_fee = total

    @api.depends('league_cell_ids.leagues_ids', 'league_cell_ids.league_leaders_ids')
    def _assign_to_main_office_league(self):
        """This function will assign leaders to total members and total fee"""
        for record in self:
            total = 0.00
            record.total_leagues = record.total_league = len(record.league_cell_ids.leagues_ids.ids) + len(record.league_cell_ids.league_leaders_ids.ids)
            if record.league_cell_ids.leagues_ids:
                exists = record.league_cell_ids.leagues_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_main_assembler'))
                if len(exists.ids) > 1:
                    raise UserError(_("You Can Only Have One Main Office Assembler"))
                exists_2 = record.league_cell_ids.leagues_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_main_finance'))
                if len(exists_2.ids) > 1:
                    raise UserError(_("You Can Only Have One Main Office Assembler"))
                for league in record.league_cell_ids.leagues_ids:
                    user = self.env['res.users'].search([('id', '=', league.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_main_finance'):
                        record.main_finance = user.id
                    if user.has_group('members_custom.member_group_main_assembler'):
                        record.main_assembler = user.id
                    total += (league.league_payment)
            if record.league_cell_ids.league_leaders_ids:
                for leader in record.league_cell_ids.league_leaders_ids:
                    total += (leader.league_payment)
            record.total_leagues_fee = record.total_league_fee = total 


    @api.depends('league_cell_ids')
    def _calculate_league_cells(self):
        """This function will calculate the total cells of main_office"""
        for record in self:
            record.total_cell_league = len(record.league_cell_ids.ids)
            all_league_leaders = record.league_cell_ids.leagues_ids.filtered(lambda rec: rec.league_responsibility.id == 3)
            record.league_leader_ids = all_league_leaders
            # exists = record.league_leader_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_main_manager'))
            # if len(exists.ids) > 1:
            #     raise UserError(_("You Can Only Have One Main Office Administrator"))
            for leader in record.league_leader_ids:
                user = self.env['res.users'].search([('id', '=', leader.user_ids._origin.id)])
                if user.has_group('members_custom.member_group_main_manager'):
                    record.main_admin = user.id                
            if record.total_cell_league > 0:
                record.cells = True
            else:
                record.cells = False
                record.total_leagues = 0
                record.total_league_fee = 0.00
                record.total_league = 0
                record.total_leagues_fee = 0.00


    @api.depends('cell_ids')
    def _calculate_cells(self):
        for record in self:
            record.total_cell = len(record.cell_ids.ids)
            all_leaders = record.cell_ids.members_ids.filtered(lambda rec: rec.member_responsibility.id == 3)
            record.leader_ids = all_leaders
            # exists = record.leader_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_main_manager'))
            # if len(exists.ids) > 1:
            #     raise UserError(_("You Can Only Have One Main Office Administrator"))
            for leader in record.leader_ids:
                user = self.env['res.users'].search([('id', '=', leader.user_ids._origin.id)])
                if user.has_group('members_custom.member_group_main_manager'):
                    record.main_admin = user.id  
            if record.total_cell > 0:
                record.cells = True
            else:
                record.cells = False
                record.total_members = 0
                record.total_member_fee = 0.00
                record.total_member = 0
                record.total_membership_fee = 0.00

    def _get_total_cell(self):
        """This function will get the total pending meetings"""
        for record in self:
            meetings = self.env['meeting.cells'].search([('main_id', '=', record.id), ('state', '=', 'pending')])
            if len(meetings) > 0:
                record.pending_meetings_cells = len(meetings)
            else:
                record.pending_meetings_cells = 0


    def _get_total(self):
        """This function will get the total pending meetings"""
        for record in self:
            meetings = self.env['meeting.each.other.main'].search([('main_id', '=', record.id), ('state', '=', 'pending')])
            if len(meetings) > 0:
                record.pending_meetings = len(meetings)
            else:
                record.pending_meetings = 0


class Cells(models.Model):
    _name="member.cells"
    _description="This model will contain the cells members will belong in"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    # def _default_main_office(self):
    #     """This function will set default value for cell"""
    #     return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).id      

    # def _default_type(self):
    #     """This function will give default value to type"""
    #     main_office = self.env['main.office'].search([('main_admin', '=', self.env.user.id)])
    #     if len(main_office.ids) > 1:
    #         raise UserError(_("You Are Registered "))
    #     if main_office.for_which_members == 'member':
    #         return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).member_main_type_id.id
    #     if main_office.for_which_members == 'league':
    #         return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).league_main_type_id     

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).wereda_id.id  

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).subcity_id.id   

    name = fields.Char(required=True, translate=True, track_visibility='onchange')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity, track_visibility='onchange', store=True)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange', store=True)
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange', string="League or Member", store=True)
    member_cell_type_id = fields.Many2one('membership.organization', track_visibility='onchange', store=True)
    league_cell_type_id = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange', store=True)
    main_office = fields.Many2one('main.office', track_visibility='onchange', store=True)
    main_office_league = fields.Many2one('main.office', track_visibility='onchange', store=True)
    members_ids = fields.Many2many('res.partner', track_visibility='onchange', store=True)
    total = fields.Integer(store=True)
    leaders_ids = fields.Many2many('res.partner', 'leader_cell_rel', string="Leaders", track_visibility='onchange', store=True)
    league_leaders_ids = fields.Many2many('res.partner', 'league_leader_cell_rel', string="League Leaders", track_visibility='onchange', store=True)
    leagues_ids = fields.Many2many('res.partner', 'league_cell_rel', string="League Members", track_visibility='onchange', store=True)
    all_partners = fields.Many2many('res.partner', 'all_partner_rel', store=True)
    total_members = fields.Integer(compute="_calculate_total_members", store=True)
    total_leaders = fields.Integer(compute="_assign_leaders_cells", store=True)
    total_leagues = fields.Integer(compute="_calculate_total_leagues", store=True)
    total_leader_leagues = fields.Integer(compute="_calculate_total_leader_leagues", store=True)
    total_leader_fee = fields.Float(store=True)
    total_member_fee = fields.Float(store=True)
    total_league_fee = fields.Float(store=True)
    total_leader_league_fee = fields.Float(store=True)
    cell_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_cell_manager").id)], readonly=True, store=True)
    cell_finance = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_finance").id)], readonly=True, store=True)
    cell_assembler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_assembler").id)], readonly=True, store=True)
    total_membership_fee = fields.Float(compute="_compute_totals", store=True)
    total = fields.Integer(compute="_all_members", store=True)
    members = fields.Boolean(default=False)
    pending_meetings = fields.Integer(compute="_get_total")
    is_mixed = fields.Boolean(default=False, string="Mixed Cell")

    _sql_constraints = [('name_constraint', 'unique(name)', 'name must be unique.'),] 

    @api.model
    def create(self, vals):
        """This function will check if the numbers added are what is estimated"""  
        res = super(Cells, self).create(vals)       
        user = self.env.user
        config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', res.for_which_members)])
        if config:
            if res.total < config.minimum_number:
                warning_message = "The Added Numbers Of Members Is " + str(res.total) + " Which Is Less Than " + str(config.minimum_number) + " According To The Rule Given."
                if config.reject:
                    raise UserError(_(warning_message))
                else:
                    user.notify_warning(warning_message, '<h4>Minimum Number of Members not Reached.</h4>', True)
            elif res.total > config.maximum_number:
                if config.reject:
                    message="The Added Numbers Of Members Is " + str(res.total) + " Which Is More Than " + str(config.maximum_number) + " According To The Rule Given."
                    raise UserError(_(message))
                else:
                    message = "The Number Of Members You Added Is Going To Exceed The Maximum Number Given In The Rule."
                    user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True) 
        else:
            raise UserError(_("Please Configure The Number of Members Allowed In A Single Cell"))
        return res

    def unlink(self):
        """This function will check if cell has any members if not it can be deleted"""
        for record in self:
            if record.members_ids and len(record.members_ids) > 0:
                raise UserError(_("You can't Delete This Cell Because It has Members In It."))
            if record.leaders_ids and len(record.leaders_ids) > 0:
                raise UserError(_("You can't Delete This Cell Because It has Leader In It."))
            if record.leagues_ids and len(record.leagues_ids) > 0:
                raise UserError(_("You can't Delete This Cell Because It has Leagues In It."))
            if record.league_leaders_ids and len(record.league_leaders_ids) > 0:
                raise UserError(_("You can't Delete This Cell Because It has League Leaders In It."))

        return super(Cells, self).unlink()

    @api.onchange('is_mixed')
    def _change_fields_after_is_mixed(self):
        """This function will make fields null based on mixed"""
        for record in self:
            if record.is_mixed:
                record.member_cell_type_id = False
                record.league_cell_type_id = False
                record.main_office = False
                record.main_office_league = False
            else:
                record.member_cell_type_id = False
                record.league_cell_type_id = False
                record.main_office = False
                record.main_office_league = False

    @api.onchange('is_mixed', 'member_cell_type_id', 'league_cell_type_id', 'for_which_members')
    def _domain_main_office(self):
        """This will create a domain based on wereda dn for which member"""
        for record in self:
            if record.wereda_id and record.member_cell_type_id and not record.is_mixed:
                return {'domain': {'main_office': [('member_main_type_id', '=', record.member_cell_type_id.id), ('wereda_id', '=', record.wereda_id.id)],
                                    'members_ids': [('membership_org','=', record.member_cell_type_id.id), ('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False), ('member_responsibility', '!=', 2), '|', ('is_member', '=', True), ('is_leader', '=', True)],
                                    'leaders_ids': [('member_responsibility', '=', 2), ('membership_org','=', record.member_cell_type_id.id), ('is_member', '=', True), ('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False)]
                                    }
                        }
            if record.wereda_id and not record.member_cell_type_id and record.is_mixed and not record.league_cell_type_id:
                return {'domain': {'main_office': [('for_which_members', '=', record.for_which_members), ('wereda_id', '=', record.wereda_id.id)],
                                    'members_ids': [('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False), ('member_responsibility', '!=', 2), '|', ('is_member', '=', True), ('is_leader', '=', True)],
                                    'leaders_ids': [('member_responsibility', '=', 2), ('is_member', '=', True), ('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False)],
                                    'main_office_league': [('for_which_members', '=', record.for_which_members), ('wereda_id', '=', record.wereda_id.id)],
                                    'league_leaders_ids': [('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '=', 2)],
                                    'leagues_ids': [('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '!=', 2)]
                                    }
                        }
            if record.wereda_id and record.league_cell_type_id and not record.is_mixed:
                return {'domain': {'main_office_league': [('league_main_type_id', '=', record.league_cell_type_id), ('wereda_id', '=', record.wereda_id.id)],
                                    'league_leaders_ids': [('league_org','=', record.league_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '=', 2)],
                                    'leagues_ids': [('league_org','=', record.league_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '!=', 2)]
                                    }
                        }


    @api.onchange('subcity_id')
    def _change_all_field_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False
                record.member_cell_type_id = False
                record.league_cell_type_id = False
                record.main_office = False
                record.main_office_league = False

    @api.onchange('wereda_id')
    def _change_all_field_after_wereda_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.wereda_id:
                record.member_cell_type_id = False
                record.league_cell_type_id = False
                record.main_office = False
                record.main_office_league = False


    @api.onchange('for_which_members')
    def _change_all_field_after_for_which_members_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.for_which_members:
                record.member_cell_type_id = False
                record.league_cell_type_id = False
                record.main_office = False
                record.main_office_league = False


    @api.onchange('member_cell_type_id')
    def _change_all_field_after_member_cell_type_id_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.member_cell_type_id:
                record.main_office = False


    @api.onchange('league_cell_type_id')
    def _change_all_field_after_league_cell_type_id_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.league_cell_type_id:
                record.main_office_league = False

    @api.onchange('leaders_ids', 'members_ids', 'league_leaders_ids', 'leagues_ids')
    def _check_total(self):
        """This function will check if the number of members added is what is according to the estimated"""
        for record in self:
            user = self.env.user
            if record.total_members or record.total_leaders or record.total_leagues or record.total_leader_leagues:
                config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
                if config:
                    # if record.total < config.minimum_number:
                    #     warning_message="The Added Numbers Of Members Is " + str(record.total) + " Which Is Less Than " + str(config.minimum_number) + " According To The Rule Given."
                    #     raise ValidationError(_(warning_message))
                    if record.total > config.maximum_number:
                        if config.reject:
                            message="The Added Numbers Of Members Is " + str(record.total) + " Which Is More Than " + str(config.maximum_number) + " According To The Rule Given."
                            raise ValidationError(_(message))
                        else:
                            message = "The Number Of Members You Added Is Going To Exceed The Maximum Number Given In The Rule."
                            user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True)

    @api.onchange('main_office')
    def _can_not_add_to_main_office(self):
        """This will check if excess cells are in main office"""
        for record in self:
            if record.main_office:
                user = self.env.user
                total_cells = len(record.main_office.cell_ids.ids)
                config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
                if config:
                    if total_cells > config.maximum_cell:
                        if config.reject:
                            message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                            raise ValidationError(_(message))
                        else:
                            message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                            user.notify_warning(message, '<h4>Maximum Numbers Of Cells Are Exceeding.</h4>', True)
                else:
                    raise UserError(_("Please Configure The Number of Cells Allowed In A Single Main Office"))

    @api.onchange('main_office_league')
    def _can_not_add_to_main_office_league(self):
        """This will check if excess cells are in main office"""
        for record in self:
            if record.main_office_league:
                user = self.env.user
                total_cells = len(record.main_office_league.league_cell_ids.ids)
                config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
                if config:
                    if total_cells > config.maximum_cell:
                        if config.reject:
                            message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                            raise ValidationError(_(message))
                        else:
                            message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                            user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True)    
                else:
                    raise UserError(_("Please Configure The Number of Cells Allowed In A Single Main Office"))


    @api.onchange('main_office', 'main_office_league', 'is_mixed')
    def _pick_a_organization(self):
        """This function will make usre an organization is picked before main office"""
        for record in self:
            if not record.is_mixed:
                if not record.member_cell_type_id and record.main_office:
                    raise ValidationError(_('Please Fill In The Member Organization First.'))
                if not record.league_cell_type_id and record.main_office_league:
                    raise ValidationError(_('Please Fill In The League Organization First.'))                                                                                                                         

    @api.depends('leaders_ids')
    def _assign_leaders_cells(self):
        """This function will assign leaders their respective main office and cells"""
        for record in self:
            total = 0.00
            record.total_leaders = len(record.leaders_ids.ids)
            if record.leaders_ids:
                # exists = record.leaders_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_cell_manager'))
                # if len(exists.ids) > 1:
                #     raise UserError(_("You Can Only Have One Cell Administrator"))
                for leader in record.leaders_ids:
                    leader.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    user = self.env['res.users'].search([('id', '=', leader.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_cell_manager'):
                        record.cell_admin = user.id
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            record.total_leader_fee = total

    @api.depends('members_ids')
    def _calculate_total_members(self):
        """This function will calculate the total members"""
        for record in self:
            total = 0.00
            record.total_members = len(record.members_ids.ids)
            if record.members_ids:
                # exists = record.members_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_assembler'))
                # if len(exists.ids) > 1:
                #     raise UserError(_("You Can Only Have One Cell Assembler"))
                # exists_2 = record.members_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_finance'))
                # if len(exists_2.ids) > 1:
                #     raise UserError(_("You Can Only Have One Cell Assembler"))
                for memb in record.members_ids:
                    memb.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    user = self.env['res.users'].search([('id', '=', memb.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_assembler') and not user.has_group('members_custom.member_group_main_assembler'):
                        record.cell_assembler = user.id
                    elif user.has_group('members_custom.member_group_finance') and not user.has_group('members_custom.member_group_main_finance'):
                        record.cell_finance = user.id                 
                    total += (memb.membership_monthly_fee_cash + memb.membership_monthly_fee_cash_from_percent)
            record.total_member_fee = total


    @api.depends('leagues_ids')
    def _calculate_total_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leagues = len(record.leagues_ids.ids)
            if record.leagues_ids:
                # exists = record.leagues_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_assembler'))
                # if len(exists.ids) > 1:
                #     raise UserError(_("You Can Only Have One Cell Assembler"))
                # exists_2 = record.leagues_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_finance'))
                # if len(exists_2.ids) > 1:
                #     raise UserError(_("You Can Only Have One Cell Assembler"))
                for league in record.leagues_ids:
                    league.write({
                        'league_main_office': record.main_office_league.id,
                        'league_member_cells': record.id
                    })
                    user = self.env['res.users'].search([('id', '=', league.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_finance') and not user.has_group('members_custom.member_group_main_finance'):
                        record.cell_finance = user.id
                    if user.has_group('members_custom.member_group_assembler') and not user.has_group('members_custom.member_group_main_assembler'):
                        record.cell_assembler = user.id
                    total += (league.league_payment)
            record.total_league_fee = total        


    @api.depends('league_leaders_ids')
    def _calculate_total_leader_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leader_leagues = len(record.league_leaders_ids.ids)
            if record.league_leaders_ids:
                # exists = record.league_leaders_ids.filtered(lambda rec: rec.user_ids.has_group('members_custom.member_group_cell_manager'))
                # if len(exists.ids) > 1:
                #     raise UserError(_("You Can Only Have One Cell Administrator"))
                for league in record.league_leaders_ids:
                    league.write({
                        'league_main_office': record.main_office_league.id,
                        'league_member_cells': record.id
                    })
                    user = self.env['res.users'].search([('id', '=', league.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_cell_manager'):
                        record.cell_admin = user.id
                    total += (league.league_payment)
            record.total_leader_league_fee = total 

    @api.depends('total_members', 'total_leaders', 'total_leagues', 'total_leader_leagues')
    def _all_members(self):
        """Collect all in one"""
        for record in self:
            if record.total_members or record.total_leaders or record.total_leagues or record.total_leader_leagues:
                record.total = record.total_members + record.total_leaders + record.total_leagues + record.total_leader_leagues
                if record.total > 0:
                    record.members = True


    @api.depends('total_leader_fee', 'total_member_fee', 'total_league_fee', 'total_leader_league_fee')
    def _compute_totals(self):
        """This function will compute the total fee and total members"""
        for record in self:
            if record.total_member_fee or record.total_leader_fee or record.total_league_fee or record.total_leader_league_fee:
                record.total_membership_fee = record.total_leader_fee + record.total_member_fee + record.total_league_fee + record.total_leader_league_fee



    def _get_total(self):
        """This function will get the total pending meetings"""
        for record in self:
            meetings = self.env['meeting.each.other'].search([('cell_id', '=', record.id), ('state', '=', 'pending')])
            if len(meetings) > 0:
                record.pending_meetings = len(meetings)
            else:
                record.pending_meetings = 0