"""This file will deal with training for leaders """

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class MembersAssembly(models.Model):
    _inherit="member.assembly"


    wereda_id = fields.Many2one('membership.handlers.branch', related="partner_id.wereda_id", store=True)
    main_office_id = fields.Many2one('main.office', related="partner_id.main_office", store=True, string="Basic Organization")
    cell_id = fields.Many2one('member.cells', related="partner_id.member_cells", store=True, string="Member Cell")
    main_office_league_id = fields.Many2one('main.office', related="partner_id.league_main_office", store=True, string="League Basic Organization")
    cell_league_id = fields.Many2one('member.cells', related="partner_id.league_member_cells", store=True, string="League Cell")