from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class SupporterStructure(models.Model):
    _name = "supporter.structure"

    _parent_name = "parent_id_2"

    name = fields.Char(required=True, string="Name", translate=True, copy=False, index=True)
    parent_id_2 = fields.Many2one('supporter.structure', string="Structure", copy=False, index=True)
    cell = fields.Many2one('member.cells', string="cell", copy=False, index=True)
    main_office = fields.Many2one('main.office', string="main_office", copy=False, index=True)
    wereda = fields.Many2one('membership.handlers.branch', string="wereda", copy=False, index=True)
    sub_city = fields.Many2one('membership.handlers.parent', string="sub city", copy=False, index=True)
    is_member = fields.Boolean("membership structure")
    is_league = fields.Boolean("league structure")
    is_supporter = fields.Boolean("league structure")
    users = fields.Many2many(
        comodel_name="res.users",
        relation="supporter_group_users_rel",
        column1="gid",
        column2="uid",
        string=" Users",
        auto_join=True,
        store=True,
    )

    def give_structure(self):

        sub_city = self.env['membership.handlers.parent'].search([])
        for sub in sub_city:
            par = self.env['supporter.structure'].search([('name', '=', sub.name)])
            if not par:
                vals = {
                    'name': sub.name,
                    'sub_city': sub.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,

                }
                res = self.env['supporter.structure'].sudo().create(vals)
        wereda = self.env['membership.handlers.branch'].search([])
        for wor in wereda:
            par_1 = self.env['supporter.structure'].search(
                [('name', '=', wor.name), ('sub_city', '=', wor.parent_id.id)])
            if not par_1:
                par = self.env['supporter.structure'].search([('name', '=', wor.parent_id.name)])
                vals = {
                    'name': wor.name,
                    'sub_city': wor.parent_id.id,
                    'parent_id_2': par.id,
                    'wereda': wor.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,

                }
                res = self.env['supporter.structure'].sudo().create(vals)
        strc = self.env['supporter.structure'].search([])
        for line in strc:
             supporte = self.env['supporter.members'].search([('id', '=', line.id)])
             candidate = self.env['candidate.members'].search([('id', '=', line.id)])
             for rec in supporte:
                 rec.struc_3 = line.id
             for rec in candidate:
                 rec.struc_3 = line.id


class CandidateMembers(models.Model):
    _inherit = 'candidate.members'

    struc_3 = fields.Many2one('supporter.structure', string="Structure", store=True,
                              domain=[('is_supporter', '=', True)])

    @api.model
    def create(self, vals):
        res = super(CandidateMembers, self).create(vals)
        try:
            if vals['wereda_id']:
                woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                par = self.env['supporter.structure'].search([('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                res.struc_3 = par.id
        except:
            return res
        return res

    def write(self, vals):
            try:
                if vals['wereda_id']:
                    woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                    print("woreda_ia", woreda_ia.id, woreda_ia.name)
                    par = self.env['supporter.structure'].search(
                        [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                    self.struc_3 = par.id
            except:
                return super(CandidateMembers, self).write(vals)
            return super(CandidateMembers, self).write(vals)


class SupporterMembers(models.Model):
    _inherit = 'supporter.members'

    struc_3 = fields.Many2one('supporter.structure', string="Structure", store=True,
                              domain=[('is_supporter', '=', True)])

    @api.model
    def create(self, vals):
        res = super(SupporterMembers, self).create(vals)
        try:
            if vals['wereda_id']:
                woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                par = self.env['supporter.structure'].search(
                    [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                res.struc_3 = par.id
        except:
            return res
        return res

    def write(self, vals):
        try:
            if vals['wereda_id']:
                woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                print("woreda_ia", woreda_ia.id, woreda_ia.name)
                par = self.env['supporter.structure'].search(
                    [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                self.struc_3 = par.id
        except:
            return super(SupporterMembers, self).write(vals)
        return super(SupporterMembers, self).write(vals)


