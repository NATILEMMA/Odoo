"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class MeetingCells(models.Model):
    _name = "meeting.cells"
    _description = "This model will handle meeting of Cells with Basic Organization"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

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
    place_of_meeting = fields.Char(translate=True, required=True, size=64)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    year = fields.Many2one('fiscal.year', default=_default_year, required=True)
    main_id = fields.Many2one('main.office', readonly=True, default=_default_main)
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], related="main_id.for_which_members")
    cell_id = fields.Many2one('member.cells', domain="[('main_office', '=', main_id), ('state', '=', 'active')]", string="Cell", required=True)
    meeting_minute = fields.Text('Meeting Minute')
    state = fields.Selection(selection=[('new', 'New'), ('pending', 'Pending'), ('started', 'Started'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], default='new')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    next_date_of_meeting = fields.Date()
    participant_counter = fields.Integer()
    note_id = fields.Text('Description')
    attachment_amount = fields.Integer(compute="_count_attachments")
                       

    @api.model
    def create(self, vals):
        """This will create the naming of the meeting"""
        res = super(MeetingCells, self).create(vals)
        if not res.date_of_meeting:
            raise UserError(_("Please Add Date of Meeting"))
        res.name = "Meeting On " + str(res.date_of_meeting)
        if res.start_time == 0.00 or res.end_time == 0.00:
            raise UserError(_("Please Add Start and End Time of Meeting"))
        if res.end_time > 11.0:
            raise UserError(_("Please Add End Time Can't Be After 11:00 LT"))
        if res.start_time > res.end_time:
            raise UserError(_("Meeting Start Time should be before End Time")) 
        if res.start_time == res.end_time:
            raise UserError(_("Meeting Start Time and End Time Shouldn't be The Same")) 
        res.state = 'pending'
        return res

    def unlink(self):
        """This function will delete meetings"""
        for record in self:
            if record.state != 'new':
                raise UserError(_("Meetings That Have Been Scheduled Can Not Be Deleted"))
        return super(MeetingCells, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'finished' or record.state == 'cancelled'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def _count_attachments(self):
        """This function will count the attchments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0

    def remind_meeting_cells(self):
        """This function will remind meeting with cells"""
        next_week = date.today() + relativedelta(weeks=1) 
        meetings = self.env['meeting.cells'].search([('next_date_of_meeting', '=', next_week)])
        for meeting in meetings:
            message = _("The Meeting Set With One of Your Cells is Due Next Week On %s") % (str(meeting.next_date_of_meeting))
            title = _("<h4>Next Meeting Is Due</h4>")
            model = self.env['ir.model'].search([('model', '=', 'meeting.cells'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Basic Organization Meeting Cells')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Next Meeting With Cells is Due",
                'date_deadline': date.today() + relativedelta(weeks=1),
                'user_id': meeting.main_id.main_assembler.id,
                'res_model_id': model.id,
                'res_id': meeting.id,
                'activity_type_id': activity_type.id
            })
            meeting.main_id.main_assembler.notify_warning(message, title, True)


    @api.onchange('date_of_meeting')
    def _change_date_of_meeting(self):
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
            if record.attachment_amount == 0:
                raise UserError(_("Please Attach Attendance Photos Before Finishing Meetings"))
            record.state = 'finished'

    def cancel_meeting(self):
        """This function will cancel a meeting"""
        for record in self:
            if not record.note_id:
                raise UserError(_("Please Add Note To Describe the Reason for Cancelling Meeting"))
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
            if record.cell_id.leagues_ids:
                for member in record.cell_id.leagues_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_with_main_office_id': record.id,
                    }) 
            if record.cell_id.league_leaders_ids:
                for member in record.cell_id.league_leaders_ids:
                    self.env['member.assembly'].sudo().create({
                        'partner_id': member.id,
                        'meeting_cell_with_main_office_id': record.id,
                    })                
            record.state = 'started'


class MeetingEachOther(models.Model):
    _name = "meeting.each.other"
    _description = "This model will handle meeting of Cells with Members"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

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
    place_of_meeting = fields.Char(translate=True, required=True, size=64)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    year = fields.Many2one('fiscal.year', default=_default_year, required=True)
    cell_id = fields.Many2one('member.cells', readonly=True, default=_default_cell)
    meeting_minute = fields.Text('Meeting Minute')
    state = fields.Selection(selection=[('new', 'New'), ('pending', 'Pending'), ('started', 'Started'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], default='new')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    next_date_of_meeting = fields.Date()
    participant_counter = fields.Integer()
    note_id = fields.Text('Description')
    attachment_amount = fields.Integer(compute="_count_attachments")


    @api.model
    def create(self, vals):
        """This will create the naming of the meeting"""
        res = super(MeetingEachOther, self).create(vals)
        if not res.date_of_meeting:
            raise UserError(_("Please Add Date of Meeting"))
        if res.start_time == 0.00 or res.end_time == 0.00:
            raise UserError(_("Please Add Start and End Time of Meeting"))
        if res.end_time > 11.0:
            raise UserError(_("Please Add End Time Can't Be After 11:00 LT"))
        if res.start_time > res.end_time:
            raise UserError(_("Meeting Start time should be before End Time")) 
        if res.start_time == res.end_time:
            raise UserError(_("Meeting Start Time and End Time Shouldn't be The Same")) 
        res.name = "Meeting On " + str(res.date_of_meeting)
        res.state = 'pending'
        return res

    def unlink(self):
        """This function will delete meetings"""
        for record in self:
            if record.state != 'new':
                raise UserError(_("Meetings That Have Been Scheduled Can Not Be Deleted"))
        return super(MeetingEachOther, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'finished' or record.state == 'cancelled'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    def _count_attachments(self):
        """This function will count the attchments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0

    def remind_meeting_each_other(self):
        """This function will remind meeting with members"""
        next_week = date.today() + relativedelta(weeks=1) 
        meetings = self.env['meeting.each.other'].search([('next_date_of_meeting', '=', next_week)])
        for meeting in meetings:
            message = _("The Meeting Set With Your Members is Due Next Week On %s") % (str(meeting.next_date_of_meeting))
            title = _("<h4>Next Meeting Is Due</h4>")
            model = self.env['ir.model'].search([('model', '=', 'meeting.each.other'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Meeting Each Other')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Next Meeting With Member is Due",
                'date_deadline': date.today() + relativedelta(weeks=1),
                'user_id': meeting.cell_id.cell_assembler.id,
                'res_model_id': model.id,
                'res_id': meeting.id,
                'activity_type_id': activity_type.id
            })
            meeting.cell_id.cell_assembler.notify_warning(message, title, True)

    @api.onchange('date_of_meeting')
    def _change_date_of_meeting(self):
        """This function will change the naming"""
        for record in self:
            if record.date_of_meeting:
                today = date.today()
                if record.date_of_meeting <= today:
                    raise UserError(_("Please A Date After Today"))
                record.name = "Meeting On " + str(record.date_of_meeting)


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
            if record.attachment_amount == 0:
                raise UserError(_("Please Attach Attendance Photos Before Finishing Meetings"))
            record.state = 'finished'

    def cancel_meeting(self):
        """This function will cancel a meeting"""
        for record in self:
            if not record.note_id:
                raise UserError(_("Please Add Note To Describe the Reason for Cancelling Meeting"))
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
    _description = "This model will handle meeting of Basic Organization with itself"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

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
    place_of_meeting = fields.Char(translate=True, required=True, size=64)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    year = fields.Many2one('fiscal.year', default=_default_year, required=True)
    main_id = fields.Many2one('main.office', readonly=True, default=_default_main)
    meeting_minute = fields.Text('Meeting Minute')
    state = fields.Selection(selection=[('new', 'New'), ('pending', 'Pending'), ('started', 'Started'), ('finished', 'Finished'), ('cancelled', 'Cancelled')], default='new')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    next_date_of_meeting = fields.Date()
    note_id = fields.Text('Description')
    attachment_amount = fields.Integer(compute="_count_attachments")


    @api.model
    def create(self, vals):
        """This will create the naming of the meeting"""
        res = super(MeetingEachOtherMain, self).create(vals)
        if not res.date_of_meeting:
            raise UserError(_("Please Add Date of Meeting"))
        if res.start_time == 0.00 or res.end_time == 0.00:
            raise UserError(_("Please Add Start and End Time of Meeting"))
        if res.end_time > 11.0:
            raise UserError(_("Please Add End Time Can't Be After 11:00 LT"))
        if res.start_time > res.end_time:
            raise UserError(_("Meeting Start time should be before End Time")) 
        if res.start_time == res.end_time:
            raise UserError(_("Meeting Start Time and End Time Shouldn't be The Same")) 
        res.name = "Meeting On " + str(res.date_of_meeting)
        res.state = 'pending'
        return res

    def unlink(self):
        """This function will delete meetings"""
        for record in self:
            if record.state != 'new':
                raise UserError(_("Meetings That Have Been Scheduled Can Not Be Deleted"))
        return super(MeetingEachOtherMain, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'finished' or record.state == 'cancelled'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def _count_attachments(self):
        """This function will count the attchments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0


    def remind_meeting_each_other_main(self):
        """This function will remind meeting with main office eachother"""
        next_week = date.today() + relativedelta(weeks=1) 
        meetings = self.env['meeting.each.other.main'].search([('next_date_of_meeting', '=', next_week)])
        for meeting in meetings:
            message = _("The Meeting Set With Your Basic Organization is Due Next Week On %s") % (str(meeting.next_date_of_meeting))
            title = _("<h4>Next Meeting Is Due</h4>") 
            model = self.env['ir.model'].search([('model', '=', 'meeting.each.other.main'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Basic Organization Meeting Each Other')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Next Meeting With Basic Organization is Due",
                'date_deadline': date.today() + relativedelta(weeks=1),
                'user_id': meeting.main_id.main_assembler.id,
                'res_model_id': model.id,
                'res_id': meeting.id,
                'activity_type_id': activity_type.id
            })
            meeting.main_id.main_assembler.notify_warning(message, title, True)

    @api.onchange('date_of_meeting')
    def _change_date_of_meeting(self):
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
            if record.attachment_amount == 0:
                raise UserError(_("Please Attach Attendance Photos Before Finishing Meetings"))
            record.state = 'finished'

    def cancel_meeting(self):
        """This function will cancel a meeting"""
        for record in self:
            if not record.note_id:
                raise UserError(_("Please Add Note To Describe the Reason for Cancelling Meeting"))
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

    _sql_constraints = [('check_maximum_minimum', 'CHECK (maximum_number > minimum_number)', 'Maximum Number of Members Should Be Greater Than Minimum')]


    @api.model
    def create(self, vals):
        """This will check if there are more than one member/league"""
        exists = self.env['cell.configuration'].search([('for_members_or_leagues', '=', vals['for_members_or_leagues'])])
        if exists:
            raise UserError(_("You Already Have A Configuration For This Type."))
        return super(MainOfficeMembersConfiguration, self).create(vals)

    @api.onchange('for_members_or_leagues')
    def _check_duplication(self):
        """This will check if the selected has been previously selected"""
        for record in self:
            exist = self.env['cell.configuration'].search([('for_members_or_leagues', '=', record.for_members_or_leagues)])
            if exist:
                raise UserError(_("Configuration for %s already Exists") % (record.for_members_or_leagues))


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


    @api.onchange('for_members_or_leagues')
    def _check_duplication(self):
        """This will check if the selected has been previously selected"""
        for record in self:
            exist = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_members_or_leagues)])
            if exist:
                raise UserError(_("Configuration for %s already Exists") % (record.for_members_or_leagues))


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

    name = fields.Char(required=True, translate=True, track_visibility='onchange', size=128)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, default=_default_subcity, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange', string="League or Member")
    member_main_type_id = fields.Many2one('membership.organization', track_visibility='onchange', required=True, string="Organization")
    cell_ids = fields.One2many('member.cells', 'main_office', readonly=True, track_visibility='onchange')
    total_cell = fields.Integer(compute="_calculate_cells", store=True)
    total_member_fee = fields.Float(compute="_assign_to_main_office", store=True)
    total_league_fee = fields.Float(compute="_assign_to_main_office_league", store=True)
    total_member = fields.Integer(compute="_assign_to_main_office", store=True)
    total_league = fields.Integer(compute="_assign_to_main_office_league", store=True)
    total_supporters = fields.Integer(compute="_get_total_supporters", store=True)
    total_candidates = fields.Integer(compute="_get_total_candidates", store=True)
    total_members = fields.Integer(compute="_assign_to_main_office", store=True, track_visibility='onchange')
    total_leagues = fields.Integer(compute="_assign_to_main_office_league", store=True)
    leader_ids = fields.Many2many('res.partner', 'leader_main_rel', readonly=True, track_visibility='onchange')
    league_leader_ids = fields.Many2many('res.partner', 'league_leader_rel', readonly=True, track_visibility='onchange')
    total_membership_fee = fields.Float(compute="_assign_to_main_office", store=True)
    total_leagues_fee = fields.Float(compute="_assign_to_main_office_league", store=True)
    cells = fields.Boolean(default=False)
    main_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_main_manager").id)], readonly=True, store=True, string="Basic Organization Leader")
    main_finance = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_main_finance").id)], readonly=True, store=True, string="Basic Organization Finance")
    main_assembler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_main_assembler").id)], readonly=True, store=True, string="Basic Organization Assembler")
    meeting_memebers_every = fields.Integer() 
    pending_meetings_cells = fields.Integer(compute="_get_total_cell") 
    pending_meetings = fields.Integer(compute="_get_total")
    duplicate = fields.Boolean(default=False)
    main_office_id = fields.Many2one('main.office', readonly=True)
     
    
    # _sql_constraints = [('name_constraint', 'UNIQUE (name)', 'Basic Organization\'s Name Must Be Unique')] 


    @api.model
    def create(self, vals):
        """This function will create main office and confim config is set"""
        res = super(MainOffice, self).create(vals)

        if res.for_which_members == 'league':
            for record in res:
                main_office = res.with_context().copy({
                    'name': res.name + '/Member/',
                    'for_which_members': 'member',
                    'duplicate': True,
                    'main_office_id': res.id
                })
                res.main_office_id = main_office.id

        name = res.name
        if res.for_which_members == 'league':
            res.name = res.subcity_id.unique_representation_code+ '/' + res.wereda_id.unique_representation_code + '/' + res.member_main_type_id.name + '/League/' + name
        if res.for_which_members == 'member':
            res.name = res.subcity_id.unique_representation_code + '/' + res.wereda_id.unique_representation_code + '/' + res.member_main_type_id.name + '/' + name

        if res.subcity_id != res.wereda_id.parent_id:
            raise UserError(_("The Woreda Selected %s Doesn't Belong In The Subcity %s") % (res.wereda_id.name, res.subcity.name))
        config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', res.for_which_members)])
        if not config:
            raise UserError(_("Please Configure The Number of Cells Allowed In A Single Basic Organization"))

        return res


    @api.onchange('subcity_id')
    def _change_all_field(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False
                record.member_main_type_id = False
                

    @api.onchange('wereda_id')
    def _change_all_field_after_wereda(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.wereda_id:
                record.member_main_type_id = False

    @api.onchange('for_which_members')
    def _chnage_all_field_after_selection(self):
        """This function will make the organization false"""
        for record in self:
            if record.for_which_members:
                record.member_main_type_id = False


    def unlink(self):
        """This function will check if cell has any cells if not it can be deleted"""
        for record in self:
            if record.cell_ids and len(record.cell_ids) > 0:
                raise UserError(_("You can't Delete This Basic Organization Because It has Cells In It."))
            if record.leader_ids and len(record.leader_ids) > 0:
                raise UserError(_("You can't Delete This Basic Organization Because It has Leaders In It."))
        return super(MainOffice, self).unlink()


    @api.depends('cell_ids.supporter_ids')
    def _get_total_supporters(self):
        """This function will get a total supporter"""
        for record in self:
            if record.cell_ids.supporter_ids:
                record.total_supporters = len(record.cell_ids.supporter_ids.ids)

    @api.depends('cell_ids.candidate_ids')
    def _get_total_candidates(self):
        """This function will get a total supporter"""
        for record in self:
            if record.cell_ids.candidate_ids:
                record.total_candidates = len(record.cell_ids.candidate_ids.ids)

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

                all_main_admin = record.cell_ids.members_ids.filtered(lambda rec: rec.member_responsibility.id == 3).ids
                all_main_finance = record.cell_ids.members_ids.filtered(lambda rec: rec.member_sub_responsibility.id == 3).ids
                all_main_assembler = record.cell_ids.members_ids.filtered(lambda rec: rec.member_sub_responsibility.id == 4).ids

                all_leaders = all_main_assembler + all_main_admin + all_main_finance

                record.leader_ids = [(5, 0, 0)]
                record.leader_ids = [(6, 0, all_leaders)]

                for member in record.cell_ids.members_ids:
                    user = self.env['res.users'].search([('id', '=', member.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_main_manager'):
                        if record.main_admin:
                            pass
                            # raise UserError(_("This Main Office Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_admin = user.id  
                    if user.has_group('members_custom.member_group_main_finance'):
                        if record.main_finance:
                            pass
                            # raise UserError(_("This Main Office Already Has a Finance. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_finance = user.id
                    if user.has_group('members_custom.member_group_main_assembler'):
                        if record.main_assembler:
                            pass
                            # raise UserError(_("This Main Office Already Has an Assembler. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_assembler = user.id
                    total += (member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent)
            record.total_membership_fee = record.total_member_fee = total

    @api.depends('cell_ids.leagues_ids', 'cell_ids.league_leaders_ids')
    def _assign_to_main_office_league(self):
        """This function will assign leaders to total members and total fee"""
        for record in self:
            total = 0.00
            record.total_leagues = record.total_league = len(record.cell_ids.leagues_ids.ids) + len(record.cell_ids.league_leaders_ids.ids)
            if record.cell_ids.leagues_ids:

                all_main_admin = record.cell_ids.leagues_ids.filtered(lambda rec: rec.league_responsibility.id == 3).ids
                all_main_finance = record.cell_ids.leagues_ids.filtered(lambda rec: rec.league_sub_responsibility.id == 3).ids
                all_main_assembler = record.cell_ids.leagues_ids.filtered(lambda rec: rec.league_sub_responsibility.id == 4).ids

                all_leaders = all_main_assembler + all_main_admin + all_main_finance

                record.league_leader_ids = [(5, 0, 0)]
                record.league_leader_ids = [(6, 0, all_leaders)]

                for league in record.cell_ids.leagues_ids:
                    user = self.env['res.users'].search([('id', '=', league.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_main_manager'):
                        if record.main_admin:
                            pass
                            # raise UserError(_("This Main Office Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_admin = user.id  
                    if user.has_group('members_custom.member_group_main_finance'):
                        if record.main_finance:
                            pass
                            # raise UserError(_("This Main Office Already Has a Finance. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_finance = user.id
                    if user.has_group('members_custom.member_group_main_assembler'):
                        if record.main_assembler:
                            pass
                            # raise UserError(_("This Main Office Already Has an Assembler. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_assembler = user.id
                    total += (league.league_payment)
            if record.cell_ids.league_leaders_ids:
                for leader in record.cell_ids.league_leaders_ids:
                    total += (leader.league_payment)
            record.total_leagues_fee = record.total_league_fee = total 


    @api.depends('cell_ids')
    def _calculate_cells(self):
        for record in self:
            record.total_cell = len(record.cell_ids.ids)

            if record.total_cell > 0:
                record.cells = True
            else:
                record.cells = False
                record.total_members = 0
                record.total_member_fee = 0.00
                record.total_member = 0
                record.total_membership_fee = 0.00
                record.total_leagues = 0
                record.total_league_fee = 0.00
                record.total_league = 0
                record.total_leagues_fee = 0.00

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
   

    def _default_main_office(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).id  

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).wereda_id.id  

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_admin', '=', self.env.user.id)], limit=1).subcity_id.id   

    name = fields.Char(required=True, translate=True, track_visibility='onchange', size=128)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, default=_default_subcity, track_visibility='onchange', store=True)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange', store=True)
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange', string="League or Member", store=True)
    member_cell_type_id = fields.Many2one('membership.organization', track_visibility='onchange', store=True, string="Organization")
    main_office = fields.Many2one('main.office', 'main_office_rel', track_visibility='onchange', store=True, default=_default_main_office, domain="[('for_which_members', '=', for_which_members), ('member_main_type_id', '=', member_cell_type_id), ('wereda_id', '=', wereda_id)]")
    main_office_mixed = fields.Many2one('main.office', track_visibility='onchange', store=True, default=_default_main_office, domain="[('for_which_members', '=', for_which_members), ('wereda_id', '=', wereda_id)]", string="Basic Organization")
    members_ids = fields.Many2many('res.partner', track_visibility='onchange', store=True, domain="[('member_sub_responsibility', '!=', 1), ('member_sub_responsibility', '!=', 2), ('member_responsibility', '!=', 2), ('membership_org','=', member_cell_type_id), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), '|', ('is_member', '=', True), ('is_leader', '=', True)]", readonly=True)
    leaders_ids = fields.Many2many('res.partner', 'leader_cell_rel', string="Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('member_sub_responsibility', '=', 1), ('member_sub_responsibility', '=', 2), ('member_responsibility', '=', 2), ('membership_org','=', member_cell_type_id), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", readonly=True)
    league_leaders_ids = fields.Many2many('res.partner', 'league_leader_cell_rel', string="League Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('league_sub_responsibility', '=', 1), ('league_sub_responsibility', '=', 2), ('league_responsibility', '=', 2), ('league_organization','=', member_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False)]", readonly=True)
    leagues_ids = fields.Many2many('res.partner', 'league_cell_rel', string="League Members", track_visibility='onchange', store=True, domain="[('league_sub_responsibility', '!=', 1), ('league_sub_responsibility', '!=', 2), ('league_responsibility', '!=', 2), ('league_organization','=', member_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False)]", readonly=True)
    members_ids_mixed = fields.Many2many('res.partner', 'member_cell_mixed_rel', track_visibility='onchange', store=True, domain="[('member_sub_responsibility', '!=', 1), ('member_sub_responsibility', '!=', 2), ('member_responsibility', '!=', 2), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), '|', ('is_member', '=', True), ('is_leader', '=', True)]", readonly=True)
    leaders_ids_mixed = fields.Many2many('res.partner', 'leader_cell_mixed_rel', string="Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('member_sub_responsibility', '=', 1), ('member_sub_responsibility', '=', 2), ('member_responsibility', '=', 2), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", readonly=True)
    league_leaders_ids_mixed = fields.Many2many('res.partner', 'league_leader_cell_mixed_rel', string="League Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('league_sub_responsibility', '=', 1), ('league_sub_responsibility', '=', 2), ('league_responsibility', '=', 2), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False)]", readonly=True)
    leagues_ids_mixed = fields.Many2many('res.partner', 'league_cell_mixed_rel', string="League Members", track_visibility='onchange', store=True, domain="[('league_sub_responsibility', '!=', 1), ('league_sub_responsibility', '!=', 2), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False), ('league_responsibility', '!=', 2)]", readonly=True)
    supporter_ids = fields.Many2many('supporter.members', store=True, string="Supporters", readonly=True)
    candidate_ids = fields.Many2many('candidate.members', store=True, string="Candidates", readonly=True)
    all_partners = fields.Many2many('res.partner', 'all_partner_rel', store=True)
    total_members = fields.Integer(compute="_calculate_total_members", store=True)
    total_leaders = fields.Integer(compute="_assign_leaders_cells", store=True)
    total_leagues = fields.Integer(compute="_calculate_total_leagues", store=True)
    total_leader_leagues = fields.Integer(compute="_calculate_total_leader_leagues", store=True)
    total_supporters = fields.Integer(compute="_compute_supporters", store=True)
    total_candidates = fields.Integer(compute="_compute_candidates", store=True)
    total_leader_fee = fields.Float(store=True, compute="_assign_leaders_cells")
    total_member_fee = fields.Float(store=True, compute="_calculate_total_members")
    total_league_fee = fields.Float(store=True, compute="_calculate_total_leagues")
    total_leader_league_fee = fields.Float(store=True, compute="_calculate_total_leader_leagues")
    cell_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_cell_manager").id)], store=True, string="Cell Leader", readonly=True)
    cell_finance = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_finance").id)], store=True, readonly=True)
    cell_assembler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_assembler").id)], store=True, readonly=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('active', 'Active')], default='draft')
    total_membership_fee = fields.Float(compute="_compute_totals", store=True)
    total = fields.Integer(compute="_all_members", store=True)
    members = fields.Boolean(default=False)
    pending_meetings = fields.Integer(compute="_get_total")
    is_mixed = fields.Boolean(default=False, string="Mixed Cell", store=True)
    activate_cell = fields.Boolean(default=False)
    duplicate = fields.Boolean(default=False)
    cell_id = fields.Many2one('member.cells', readonly=True)


    # _sql_constraints = [('name_constraint', 'UNIQUE (name)', 'Cell\'s Name Must Be Unique')] 


    @api.model
    def create(self, vals):
        """This function will check if the numbers added are what is estimated"""  
        res = super(Cells, self).create(vals)

        if res.for_which_members == 'league':
            for record in res:
                cell = res.with_context().copy({
                    'name': res.name + '/Member/',
                    'for_which_members': 'member',
                    'duplicate': True,
                    'cell_id': res.id,
                    'main_office': res.main_office.main_office_id.id,
                    'main_office_mixed': res.main_office_mixed.main_office_id.id,
                })
                res.cell_id = cell.id

        name = res.name
        if res.for_which_members == 'league':
            res.name = res.subcity_id.unique_representation_code + '/' + res.wereda_id.unique_representation_code + '/' + res.member_cell_type_id.name + '/League/' + name
        if res.for_which_members == 'member':
            res.name = res.subcity_id.unique_representation_code + '/' + res.wereda_id.unique_representation_code + '/' + res.member_cell_type_id.name + '/' + name


        # user = self.env.user
        # config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', res.for_which_members)])
        # if config:
        #     if res.total < config.minimum_number:
        #         if config.reject:
        #             raise UserError(_("The Added Numbers Of Members Is Less Than The Rule Given."))
        #         else:
        #             message = _("The Added Numbers Of Members Is Less Than The Rule Given.")
        #             title = _("<h4>Minimum Number of Members not Reached.</h4>")
        #             user.notify_warning(message, title, True)
        #     elif res.total > config.maximum_number:
        #         message = _("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule.")
        #         if config.reject:
        #             raise UserError(_("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule."))
        #         else:
        #             title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
        #             user.notify_warning(message, title, True) 
        # else:
        #     raise UserError(_("Please Configure The Number of Members Allowed In A Single Cell"))
        # if res.for_which_members != res.main_office.for_which_members:
        #     raise UserError(_("The Type selected %s is not of The Type of Basic Organization %s") % (res.for_which_members, res.main_office.for_which_members))
        if res.member_cell_type_id.id != res.main_office.member_main_type_id.id:
            raise UserError(_("The Type of Organization selected %s is not of The Type of Organization of the Basic Organization %s") % (res.member_cell_type_id.name, res.main_office.member_main_type_id.name))
        if res.wereda_id.id != res.main_office.wereda_id.id:
            raise UserError(_("The Woreda Selected %s is not of Woreda of the Basic Organization %s") % (res.wereda_id.name, res.main_office.wereda_id.name))
        if res.subcity_id.id != res.main_office.subcity_id.id:
            raise UserError(_("The Subcity Selected %s is not of Subcity of the Basic Organization %s") % (res.subcity_id.name, res.main_office.subcity_id.name))

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
                record.main_office = False
                record.main_office_mixed = False
            else:
                record.member_cell_type_id = False
                record.main_office = False
                record.main_office_mixed = False


    # @api.onchange('is_mixed', 'member_cell_type_id', 'for_which_members', 'find_domain')
    # def _domain_main_office(self):
    #     """This will create a domain based on wereda dn for which member"""
    #     for record in self:
    #         if record.wereda_id and record.member_cell_type_id and not record.is_mixed:
    #             return {'domain': {'main_office': [('for_which_members', '=', record.for_which_members), ('member_main_type_id', '=', record.member_cell_type_id.id), ('wereda_id', '=', record.wereda_id.id)],
    #                                 'members_ids': [('membership_org','=', record.member_cell_type_id.id), ('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False), ('member_responsibility', '!=', 2), '|', ('is_member', '=', True), ('is_leader', '=', True)],
    #                                 'leaders_ids': [('member_responsibility', '=', 2), ('membership_org','=', record.member_cell_type_id.id), ('is_member', '=', True), ('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False)],
    #                                 'league_leaders_ids': [('league_organization','=', record.member_cell_type_id.id), ('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '=', 32)],
    #                                 'leagues_ids': [('league_organization','=', record.member_cell_type_id.id), ('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '!=', 32)]
    #                               }
    #                     }
    #         if record.wereda_id and not record.member_cell_type_id and record.is_mixed:
    #             return {'domain': {'main_office': [('for_which_members', '=', record.for_which_members), ('wereda_id', '=', record.wereda_id.id)],
    #                                 'members_ids': [('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False), ('member_responsibility', '!=', 2), '|', ('is_member', '=', True), ('is_leader', '=', True)],
    #                                 'leaders_ids': [('member_responsibility', '=', 2), ('is_member', '=', True), ('wereda_id', '=', record.wereda_id.id), ('member_cells', '=', False)],
    #                                 'league_leaders_ids': [('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '=', 32)],
    #                                 'leagues_ids': [('is_league', '=', True), ('wereda_id', '=', record.wereda_id.id), ('league_member_cells', '=', False), ('league_responsibility', '!=', 32)]
    #                                 }
    #                     }



    @api.onchange('subcity_id')
    def _change_all_field_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False
                record.member_cell_type_id = False
                record.main_office = False
                record.main_office_mixed = False

    @api.onchange('wereda_id')
    def _change_all_field_after_wereda_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.wereda_id:
                record.member_cell_type_id = False
                record.main_office = False
                record.main_office_mixed = False


    @api.onchange('for_which_members')
    def _change_all_field_after_for_which_members_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.for_which_members:
                record.member_cell_type_id = False
                record.main_office = False
                record.main_office_mixed = False

    @api.onchange('member_cell_type_id')
    def _change_all_field_after_member_cell_type_id_for_cell(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.member_cell_type_id:
                record.main_office = False
                record.main_office_mixed = False

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
                            raise ValidationError(_("The Added Numbers Of Members Added Is More Than The Rule Given."))
                        else:
                            message = _("The Added Numbers Of Members Added Is More Than The Rule Given.")
                            title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
                            user.notify_warning(message, title, True)

    @api.onchange('main_office_mixed')
    def _main_office_mixed_exchange(self):
        """This function will give to main office"""
        for record in self:
            record.main_office = record.main_office_mixed

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
                            raise ValidationError(_("The Added Numbers Of Cells Under This Basic Organization Is More Than The Rule Given."))
                        else:
                            message = _("The Added Numbers Of Cells Under This Basic Organization Is More Than The Rule Given.")
                            title = _("<h4>Maximum Numbers Of Cells Are Exceeding.</h4>")
                            user.notify_warning(message, title, True)
                else:
                    raise UserError(_("Please Configure The Number of Cells Allowed In A Single Basic Organization"))


    @api.onchange('main_office', 'is_mixed')
    def _pick_a_organization(self):
        """This function will make usre an organization is picked before main office"""
        for record in self:
            if not record.is_mixed:
                if not record.member_cell_type_id and record.main_office:
                    raise ValidationError(_('Please Fill In The Member Organization First.'))                                                                                                                      

    @api.onchange('leaders_ids_mixed')
    def _assign_mixed_leader(self):
        """This function will add to the leader mixed"""
        for record in self:
            record.leaders_ids = [(5, 0, 0)]
            record.leaders_ids = [(6, 0, record.leaders_ids_mixed.ids)]


    @api.depends('leaders_ids')
    def _assign_leaders_cells(self):
        """This function will assign leaders their respective main office and cells"""
        for record in self:
            total = 0.00
            record.total_leaders = len(record.leaders_ids.ids)
            if record.leaders_ids:
                for leader in record.leaders_ids:
                    if record.state == 'active':
                        leader.write({
                            'main_office': record.main_office.id,
                            'member_cells': record.id
                        })
                    user = self.env['res.users'].search([('id', '=', leader.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_cell_manager') and not user.has_group('members_custom.member_group_main_manager'):
                        if record.cell_admin:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_admin = user.id
                    if user.has_group('members_custom.member_group_finance') and not user.has_group('members_custom.member_group_main_finance'):
                        if record.cell_finance:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_finance = user.id
                    if user.has_group('members_custom.member_group_assembler') and not user.has_group('members_custom.member_group_main_assembler'):
                        if record.cell_assembler:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_assembler = user.id
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            record.total_leader_fee = total

    @api.onchange('members_ids_mixed')
    def _assign_mixed_member(self):
        """This function will add to the leader mixed"""
        for record in self:
            record.members_ids = [(5, 0, 0)]
            record.members_ids = [(6, 0, record.members_ids_mixed.ids)]

    @api.depends('members_ids')
    def _calculate_total_members(self):
        """This function will calculate the total members"""
        for record in self:
            total = 0.00
            record.total_members = len(record.members_ids.ids)
            if record.members_ids:
                for memb in record.members_ids:
                    if record.state == 'active':
                        memb.write({
                            'main_office': record.main_office.id,
                            'member_cells': record.id
                        })                
                    total += (memb.membership_monthly_fee_cash + memb.membership_monthly_fee_cash_from_percent)
            record.total_member_fee = total


    @api.onchange('leagues_ids_mixed')
    def _assign_mixed_league(self):
        """This function will add to the leader mixed"""
        for record in self:
            record.leagues_ids = [(5, 0, 0)]
            record.leagues_ids = [(6, 0, record.leagues_ids_mixed.ids)]

    @api.depends('leagues_ids')
    def _calculate_total_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leagues = len(record.leagues_ids.ids)
            if record.leagues_ids:
                for league in record.leagues_ids:
                    if record.state == 'active':
                        league.write({
                            'league_main_office': record.main_office.id,
                            'league_member_cells': record.id
                        })
                    total += (league.league_payment)
            record.total_league_fee = total        

    @api.onchange('league_leaders_ids_mixed')
    def _assign_mixed_league_leader(self):
        """This function will add to the leader mixed"""
        for record in self:
            record.league_leaders_ids = [(5, 0, 0)]
            record.league_leaders_ids = [(6, 0, record.league_leaders_ids_mixed.ids)]

    @api.depends('league_leaders_ids')
    def _calculate_total_leader_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leader_leagues = len(record.league_leaders_ids.ids)
            if record.league_leaders_ids:
                for league in record.league_leaders_ids:
                    if record.state == 'active':
                        league.write({
                            'league_main_office': record.main_office.id,
                            'league_member_cells': record.id
                        })
                    user = self.env['res.users'].search([('id', '=', league.user_ids._origin.id)])
                    if user.has_group('members_custom.member_group_cell_manager') and not user.has_group('members_custom.member_group_main_manager'):
                        if record.cell_admin:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_admin = user.id
                    if user.has_group('members_custom.member_group_finance') and not user.has_group('members_custom.member_group_main_finance'):
                        if record.cell_finance:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_finance = user.id
                    if user.has_group('members_custom.member_group_assembler') and not user.has_group('members_custom.member_group_main_assembler'):
                        if record.cell_assembler:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_assembler = user.id
                    total += (league.league_payment)
            record.total_leader_league_fee = total 

    @api.depends('supporter_ids')
    def _compute_supporters(self):
        """This function will compute the total supporters in the cell"""
        for record in self:
            record.total_supporters = len(record.supporter_ids.ids)


    @api.depends('candidate_ids')
    def _compute_candidates(self):
        """This function will compute the total candidates in the cell"""
        for record in self:
            record.total_candidates = len(record.candidate_ids.ids)

    @api.depends('total_members', 'total_leaders', 'total_leagues', 'total_leader_leagues')
    def _all_members(self):
        """Collect all in one"""
        for record in self:
            if record.total_members or record.total_leaders or record.total_leagues or record.total_leader_leagues:
                record.total = record.total_members + record.total_leaders + record.total_leagues + record.total_leader_leagues
                if record.total > 0:
                    record.members = True
                    config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
                    if config:
                        if record.total >= config.minimum_number:
                            record.activate_cell = True
                    else:
                        raise UserError(_("Please Configure The Number of Members Allowed In A Single Cell"))


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


    def activate_cell_now(self):
        """This function will activate a cell"""
        for record in self:
            config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
            if config:
                if record.total > config.maximum_number:
                    if config.reject:
                        raise UserError(_("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule."))
                    else:
                        message = _("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule.")
                        title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
                        self.env.user.notify_warning(message, title, True) 
            else:
                raise UserError(_("Please Configure The Number of Members Allowed In A Single Cell"))
            for member in record.members_ids:
                member.write({
                    'main_office': record.main_office.id,
                    'member_cells': record.id
                })
            for leader in record.leaders_ids:
                leader.write({
                    'main_office': record.main_office.id,
                    'member_cells': record.id
                })
            for league in record.league_leaders_ids:
                league.write({
                    'league_main_office': record.main_office.id,
                    'league_member_cells': record.id
                })
            for league in record.leagues_ids:
                league.write({
                    'league_main_office': record.main_office.id,
                    'league_member_cells': record.id
                })
            record.state = 'active'