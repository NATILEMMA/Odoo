"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta



class MainOfficeMembersConfiguration(models.Model):
    _name = "cell.configuration"
    _description = "This model will handle the configuration of member amount in main office"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    for_members_or_leagues = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], required=True)
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

    for_members_or_leagues = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], required=True)
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