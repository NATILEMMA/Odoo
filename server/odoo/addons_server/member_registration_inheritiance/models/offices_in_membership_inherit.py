"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class MainOffice(models.Model):
    _inherit="main.office"

    total_supporters = fields.Integer(compute="_get_total_supporters", store=True)
    total_candidates = fields.Integer(compute="_get_total_candidates", store=True)


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


class Cells(models.Model):
    _inherit="member.cells"
   
    supporter_ids = fields.Many2many('supporter.members', string="Supporters", readonly=True)
    candidate_ids = fields.Many2many('candidate.members', string="Candidates", readonly=True)
    total_supporters = fields.Integer(compute="_compute_supporters", store=True)
    total_candidates = fields.Integer(compute="_compute_candidates", store=True)



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
