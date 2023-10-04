"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class MeetingCells(models.Model):
    _inherit = "meeting.cells"

                       
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
    _inherit = "meeting.each.other"


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