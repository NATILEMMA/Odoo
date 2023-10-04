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


    # def start_meeting(self):
    #     """This function will start a meeting"""
    #     for record in self:
    #         if record.cell_id.members_ids:
    #             for member in record.cell_id.members_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_with_main_office_id': record.id,
    #                 })
    #         if record.cell_id.leaders_ids:
    #             for member in record.cell_id.leaders_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_with_main_office_id': record.id,
    #                 }) 
    #         if record.cell_id.leagues_ids:
    #             for member in record.cell_id.leagues_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_with_main_office_id': record.id,
    #                 }) 
    #         if record.cell_id.league_leaders_ids:
    #             for member in record.cell_id.league_leaders_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_with_main_office_id': record.id,
    #                 })                
    #         record.state = 'started'


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


    # def start_meeting(self):
    #     """This function will start a meeting"""
    #     for record in self:
    #         if record.cell_id.members_ids:
    #             for member in record.cell_id.members_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_together_id': record.id,
    #                 })
    #         if record.cell_id.leaders_ids:
    #             for member in record.cell_id.leaders_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_together_id': record.id,
    #                 }) 
    #         if record.cell_id.leagues_ids:
    #             for member in record.cell_id.leagues_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_together_id': record.id,
    #                 }) 
    #         if record.cell_id.league_leaders_ids:
    #             for member in record.cell_id.league_leaders_ids:
    #                 self.env['member.assembly'].sudo().create({
    #                     'partner_id': member.id,
    #                     'meeting_cell_together_id': record.id,
    #                 })                
    #         record.state = 'started'


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