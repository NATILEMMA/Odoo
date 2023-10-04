from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta



class LeagueStructure(models.Model):
    _name = "league.structure"

    _parent_name = "parent_id_2"

    name = fields.Char(required=True, string="Name", translate=True, copy=False, index=True)
    parent_id_2 = fields.Many2one('league.structure', string="Structure", copy=False, index=True)
    cell = fields.Many2one('member.cells', string="cell", copy=False, index=True)
    main_office = fields.Many2one('main.office', string="main_office", copy=False, index=True)
    wereda = fields.Many2one('membership.handlers.branch', string="wereda", copy=False, index=True)
    sub_city = fields.Many2one('membership.handlers.parent', string="sub city", copy=False, index=True)
    is_member = fields.Boolean("membership structure")
    is_league = fields.Boolean("league structure")
    is_supporter = fields.Boolean("league structure")
    users = fields.Many2many(
        comodel_name="res.users",
        relation="league_structure_group_users_rel",
        column1="gid",
        column2="uid",
        string=" Users",
        auto_join=True,
        store=True,
    )

    def give_structure(self):

        sub_city = self.env['membership.handlers.parent'].search([])
        for sub in sub_city:
            par = self.env['league.structure'].search([('name', '=', sub.name)])
            if not par:
                vals = {
                    'name': sub.name,
                    'sub_city': sub.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,

                }
                res = self.env['league.structure'].sudo().create(vals)
        wereda = self.env['membership.handlers.branch'].search([])
        for wor in wereda:
            par_1 = self.env['league.structure'].search([('name', '=', wor.name), ('sub_city', '=', wor.parent_id.id)])
            if not par_1:
                par = self.env['league.structure'].search([('name', '=', wor.parent_id.name)])
                vals = {
                    'name': wor.name,
                    'sub_city': wor.parent_id.id,
                    'parent_id_2': par.id,
                    'wereda': wor.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,

                }
                res = self.env['league.structure'].sudo().create(vals)
        main_office = self.env['main.office'].search([])
        for main in main_office:
            par_2 = self.env['league.structure'].search(
                [('name', '=', main.name), ('wereda', '=', main.wereda_id.id),
                 ('sub_city', '=', main.wereda_id.parent_id.id)])
            if not par_2:
                par = self.env['league.structure'].search(
                    [('sub_city', '=', main.wereda_id.parent_id.id), ('wereda', '=', main.wereda_id.id),
                     ('name', '=', main.wereda_id.name)])
                if main.for_which_members == 'league':
                    vals = {
                        'name': main.name,
                        'sub_city': main.wereda_id.parent_id.id,
                        'parent_id_2': par.id,
                        'wereda': main.wereda_id.id,
                        'main_office': main.id,
                        'is_league': True

                    }
                    res = self.env['league.structure'].sudo().create(vals)
        cells = self.env['member.cells'].search([])
        for cell in cells:
            if cell.for_which_members == 'member':
                cell_main_office = cell.main_office
            if cell.for_which_members == 'league':
                cell_main_office = cell.main_office_league

            par_2 = self.env['league.structure'].search(
                [('name', '=', cell.name), ('main_office', '=', cell_main_office.id),
                 ('wereda', '=', cell.wereda_id.id), ('sub_city', '=', cell.wereda_id.parent_id.id)])
            if not par_2:
                par = self.env['league.structure'].search(
                    [('name', '=', cell_main_office.name), ('main_office', '=', cell.main_office.id),
                     ('wereda', '=', cell.wereda_id.id), ('sub_city', '=', cell.wereda_id.parent_id.id)])
                if cell.main_office_league:
                    vals = {
                        'name': cell.name,
                        'sub_city': cell_main_office.wereda_id.parent_id.id,
                        'parent_id_2': par.id,
                        'wereda': cell_main_office.wereda_id.id,
                        'main_office': cell_main_office.id,
                        'cell': cell.id,
                        'is_member': True

                    }
                    res = self.env['league.structure'].sudo().create(vals)
            par_2 = self.env['league.structure'].search([])
            for line in par_2:
               if line.cell.id:
                 partner = self.env['res.partner'].search([('league_member_cells', '=', line.cell.id)])
                 for par in partner:
                     par.struc_2 = line.id
               if not line.cell.id and line.wereda.id:
                   partner = self.env['res.partner'].search([('subcity_id', '=', line.wereda.id)])
                   for par in partner:
                       par.struc_2 = line.id









