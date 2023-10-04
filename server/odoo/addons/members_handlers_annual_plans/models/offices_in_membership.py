"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


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

    name = fields.Char(store=True, translate=True)
    name_2 = fields.Char(required=True, translate=True, track_visibility='onchange', size=128, store=True, string="Name 2")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, default=_default_subcity, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange', string="League or Member")
    league_type = fields.Selection(selection=[('young', 'Youngster'), ('women', 'Woman')], track_visibility='onchange')
    member_main_type_id = fields.Many2one('membership.organization', track_visibility='onchange', required=True, string="Organization")
    cell_ids = fields.One2many('member.cells', 'main_office', readonly=True, track_visibility='onchange')
    total_cell = fields.Integer(compute="_calculate_cells", store=True)
    total_member_fee = fields.Float(compute="_assign_to_main_office", store=True)
    total_league_fee = fields.Float(compute="_assign_to_main_office_league", store=True)
    total_member = fields.Integer(compute="_assign_to_main_office", store=True)
    total_league = fields.Integer(compute="_assign_to_main_office_league", store=True)
    total_members = fields.Integer(compute="_assign_to_main_office", store=True, track_visibility='onchange')
    total_leagues = fields.Integer(compute="_assign_to_main_office_league", store=True)
    leader_ids = fields.Many2many('res.partner', 'leader_main_rel', readonly=True, track_visibility='onchange')
    league_leader_ids = fields.Many2many('res.partner', 'league_leader_rel', readonly=True, track_visibility='onchange')
    total_membership_fee = fields.Float(compute="_assign_to_main_office", store=True)
    total_leagues_fee = fields.Float(compute="_assign_to_main_office_league", store=True)
    cells = fields.Boolean(default=False)
    main_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_main_manager").id)], readonly=True, store=True, string="Basic Organization Leader")
    main_finance = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_main_finance").id)], readonly=True, store=True, string="Basic Organization Finance")
    main_assembler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_main_assembler").id)], readonly=True, store=True, string="Basic Organization Assembler")
    meeting_memebers_every = fields.Integer() 
    pending_meetings_cells = fields.Integer(compute="_get_total_cell") 
    pending_meetings = fields.Integer(compute="_get_total")
    duplicate = fields.Boolean(default=False)
    main_office_id = fields.Many2one('main.office', readonly=True)
    saved = fields.Boolean(default=False)
     

    @api.model
    def create(self, vals):
        """This function will create main office and confim config is set"""
        subcity = self.env['membership.handlers.parent'].search([('id', '=', vals['subcity_id'])])
        woreda = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
        cell_type = self.env['membership.organization'].search([('id', '=', vals['member_main_type_id'])])

        if subcity.id != woreda.parent_id.id:
            raise UserError(_("The Woreda Selected %s Doesn't Belong In The Subcity %s") % (woreda.name, subcity.name))
        if vals.get('for_which_members') == 'league' and not vals.get('league_type'):
            raise UserError(_("Please Add League Type for League Main Office %s") % (vals['name_2']))

        naming = ''
        naming_amh = ''

        if vals['for_which_members'] == 'league' and vals['league_type'] == 'young':
            naming = woreda.with_context(lang='en_US').name + '/' + cell_type.with_context(lang='en_US').name + '/Youngster/' + vals['name_2']
            naming_amh = woreda.with_context(lang='am_ET').name + '/' + cell_type.with_context(lang='am_ET').name + '/ወጣት ሊግ/' + vals['name_2']
        if vals['for_which_members'] == 'league' and vals['league_type'] == 'women':
            naming = woreda.with_context(lang='en_US').name + '/' + cell_type.with_context(lang='en_US').name + '/Woman/' + vals['name_2']
            naming_amh = woreda.with_context(lang='am_ET').name + '/' + cell_type.with_context(lang='am_ET').name + '/ሴት ሊግ/' + vals['name_2']
        if vals['for_which_members'] == 'member':
            naming = woreda.with_context(lang='en_US').name + '/' + cell_type.with_context(lang='en_US').name + '/Member/' + vals['name_2']
            naming_amh = woreda.with_context(lang='am_ET').name + '/' + cell_type.with_context(lang='am_ET').name + '/አባል/' + vals['name_2']


        current_lang = self.env.context.get('lang')
        if current_lang == 'am_ET':
            test = self.env['main.office'].with_context(lang='am_ET').search([('name', '=', naming_amh)])
            if test:
                raise UserError(_("A Main Office With Name %s Organization %s Woreda %s Already Exists") % (vals['name_2'], cell_type.name, woreda.name))

        if current_lang == 'en_US':
            test = self.env['main.office'].with_context(lang='en_US').search([('name', '=', naming)])
            if test:
                raise UserError(_("A Main Office With This Name Already Exists %s") % (vals['name_2']))

        res = super(MainOffice, self).create(vals)


        res.saved = True
        if res.for_which_members == 'league':
            for record in res:
                main_office = res.with_context().copy({
                    'name': res.name_2 + '/Member/',
                    'for_which_members': 'member',
                    'duplicate': True,
                    'main_office_id': res.id
                })
                res.main_office_id = main_office.id

        name = res.name_2
        if res.for_which_members == 'league' and res.league_type == 'young':
            res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_main_type_id.with_context(lang='en_US').name + '/Youngster/' + name
            res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_main_type_id.with_context(lang='am_ET').name + '/ወጣት ሊግ/' + name
        if res.for_which_members == 'league' and res.league_type == 'women':
            res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_main_type_id.with_context(lang='en_US').name + '/Woman/' + name
            res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_main_type_id.with_context(lang='am_ET').name + '/ሴት ሊግ/' + name
        if res.for_which_members == 'member' and not res.duplicate:
            res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_main_type_id.with_context(lang='en_US').name + '/Member/' + name
            res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + name
        if res.for_which_members == 'member' and res.duplicate:
            if res.league_type == 'young':
                res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_main_type_id.with_context(lang='en_US').name + '/Member/' + 'Youngster/' + name
                res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + 'ወጣት ሊግ/' + name
            if res.league_type == 'women':
                res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_main_type_id.with_context(lang='en_US').name + '/Member/' + 'Woman/' + name
                res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + 'ሴት ሊግ/' + name


        config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', res.for_which_members)])
        if not config:
            raise UserError(_("Please Configure The Number of Cells Allowed In A Single Basic Organization"))

        return res


    @api.onchange('name_2', 'subcity_id', 'wereda_id', 'for_which_members', 'member_main_type_id', 'league_type')
    def _change_name(self):
        """This function will change name"""
        for record in self:
            if record.name_2 and record.subcity_id and record.wereda_id and record.member_main_type_id:
                name = record.name_2
                if record.for_which_members == 'league' and record.league_type == 'young':
                    record.main_office_id.write({
                        'subcity_id': record.subcity_id.id,
                        'wereda_id': record.wereda_id.id,
                        'for_which_members': record.for_which_members,
                        'member_main_type_id': record.member_main_type_id.id,
                    })
                    record.main_office_id.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Member/' + record.name_2
                    record.main_office_id.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + record.name_2
                    record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Youngster/' + record.name_2
                    record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/ወጣት ሊግ/' + record.name_2
                if record.for_which_members == 'league' and record.league_type == 'women':
                    record.main_office_id.write({
                        'subcity_id': record.subcity_id.id,
                        'wereda_id': record.wereda_id.id,
                        'for_which_members': record.for_which_members,
                        'member_main_type_id': record.member_main_type_id.id,
                    })
                    record.main_office_id.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Member/' + record.name_2
                    record.main_office_id.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + record.name_2
                    record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Woman/' + record.name_2
                    record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/ሴት ሊግ/' + record.name_2
                if record.for_which_members == 'member' and not record.duplicate:
                    record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Member/' + record.name_2
                    record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + record.name_2
                if record.for_which_members == 'member' and record.duplicate:
                    if record.league_type == 'young':
                        record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Member/' + 'Youngster/' + record.name_2
                        record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + 'ወጣት ሊግ/' + record.name_2
                    if record.league_type == 'women':
                        record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_main_type_id.with_context(lang='en_US').name + '/Member/' + 'Woman/' + record.name_2
                        record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_main_type_id.with_context(lang='am_ET').name + '/አባል/' + 'ሴት ሊግ/' + record.name_2


                record.saved = True

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
                    if user.has_group('member_minor_configuration.member_group_main_manager'):
                        if record.main_admin:
                            pass
                            # raise UserError(_("This Main Office Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_admin = user.id  
                    if user.has_group('member_minor_configuration.member_group_main_finance'):
                        if record.main_finance:
                            pass
                            # raise UserError(_("This Main Office Already Has a Finance. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_finance = user.id
                    if user.has_group('member_minor_configuration.member_group_main_assembler'):
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
                    if user.has_group('member_minor_configuration.member_group_main_manager'):
                        if record.main_admin:
                            pass
                            # raise UserError(_("This Main Office Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_admin = user.id  
                    if user.has_group('member_minor_configuration.member_group_main_finance'):
                        if record.main_finance:
                            pass
                            # raise UserError(_("This Main Office Already Has a Finance. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.main_finance = user.id
                    if user.has_group('member_minor_configuration.member_group_main_assembler'):
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

    def update_name(self):
        """This function will update name of basic organization"""
        for record in self:
            record.saved = False


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

    name = fields.Char(store=True, translate=True)
    name_2 = fields.Char(required=True, translate=True, track_visibility='onchange', size=128, store=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, default=_default_subcity, track_visibility='onchange', store=True)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange', store=True)
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange', string="League or Member", store=True)
    league_type = fields.Selection(selection=[('young', 'Youngster'), ('women', 'Woman')], track_visibility='onchange')
    member_cell_type_id = fields.Many2one('membership.organization', track_visibility='onchange', store=True, string="Organization")
    main_office = fields.Many2one('main.office', 'main_office_rel', track_visibility='onchange', store=True, default=_default_main_office, domain="[('league_type', '=', league_type), ('for_which_members', '=', for_which_members), ('member_main_type_id', '=', member_cell_type_id), ('wereda_id', '=', wereda_id)]")
    main_office_mixed = fields.Many2one('main.office', track_visibility='onchange', store=True, default=_default_main_office, domain="[('league_type', '=', league_type), ('for_which_members', '=', for_which_members), ('wereda_id', '=', wereda_id)]", string="Basic Organization")
    members_ids = fields.Many2many('res.partner', track_visibility='onchange', store=True, domain="[('member_sub_responsibility', '!=', 1), ('member_sub_responsibility', '!=', 2), ('member_responsibility', '!=', 2), ('membership_org','=', member_cell_type_id), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), '|', ('is_member', '=', True), ('is_leader', '=', True)]", readonly=True)
    leaders_ids = fields.Many2many('res.partner', 'leader_cell_rel', string="Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('member_sub_responsibility', '=', 1), ('member_sub_responsibility', '=', 2), ('member_responsibility', '=', 2), ('membership_org','=', member_cell_type_id), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", readonly=True)
    league_leaders_ids = fields.Many2many('res.partner', 'league_leader_cell_rel', string="League Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('league_sub_responsibility', '=', 1), ('league_sub_responsibility', '=', 2), ('league_responsibility', '=', 2), ('league_organization','=', member_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False)]", readonly=True)
    leagues_ids = fields.Many2many('res.partner', 'league_cell_rel', string="League Members", track_visibility='onchange', store=True, domain="[('league_sub_responsibility', '!=', 1), ('league_sub_responsibility', '!=', 2), ('league_responsibility', '!=', 2), ('league_organization','=', member_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False)]", readonly=True)
    members_ids_mixed = fields.Many2many('res.partner', 'member_cell_mixed_rel', track_visibility='onchange', store=True, domain="[('member_sub_responsibility', '!=', 1), ('member_sub_responsibility', '!=', 2), ('member_responsibility', '!=', 2), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), '|', ('is_member', '=', True), ('is_leader', '=', True)]", readonly=True)
    leaders_ids_mixed = fields.Many2many('res.partner', 'leader_cell_mixed_rel', string="Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('member_sub_responsibility', '=', 1), ('member_sub_responsibility', '=', 2), ('member_responsibility', '=', 2), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", readonly=True)
    league_leaders_ids_mixed = fields.Many2many('res.partner', 'league_leader_cell_mixed_rel', string="League Leaders", track_visibility='onchange', store=True, domain="['&', '|', '|', ('league_sub_responsibility', '=', 1), ('league_sub_responsibility', '=', 2), ('league_responsibility', '=', 2), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False)]", readonly=True)
    leagues_ids_mixed = fields.Many2many('res.partner', 'league_cell_mixed_rel', string="League Members", track_visibility='onchange', store=True, domain="[('league_sub_responsibility', '!=', 1), ('league_sub_responsibility', '!=', 2), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False), ('league_responsibility', '!=', 2)]", readonly=True)
    all_partners = fields.Many2many('res.partner', 'all_partner_rel', store=True)
    total_members = fields.Integer(compute="_calculate_total_members", store=True)
    total_leaders = fields.Integer(compute="_assign_leaders_cells", store=True)
    total_leagues = fields.Integer(compute="_calculate_total_leagues", store=True)
    total_leader_leagues = fields.Integer(compute="_calculate_total_leader_leagues", store=True)
    total_leader_fee = fields.Float(store=True, compute="_assign_leaders_cells")
    total_member_fee = fields.Float(store=True, compute="_calculate_total_members")
    total_league_fee = fields.Float(store=True, compute="_calculate_total_leagues")
    total_leader_league_fee = fields.Float(store=True, compute="_calculate_total_leader_leagues")
    cell_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_cell_manager").id)], store=True, string="Cell Leader", readonly=True)
    cell_finance = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_finance").id)], store=True, readonly=True)
    cell_assembler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("member_minor_configuration.member_group_assembler").id)], store=True, readonly=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('active', 'Active')], default='draft')
    total_membership_fee = fields.Float(compute="_compute_totals", store=True)
    total = fields.Integer(compute="_all_members", store=True)
    members = fields.Boolean(default=False)
    pending_meetings = fields.Integer(compute="_get_total")
    is_mixed = fields.Boolean(default=False, string="Mixed Cell", store=True)
    activate_cell = fields.Boolean(default=False)
    duplicate = fields.Boolean(default=False)
    cell_id = fields.Many2one('member.cells', readonly=True)
    saved = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        """This function will check if the numbers added are what is estimated"""  
        subcity = self.env['membership.handlers.parent'].search([('id', '=', vals['subcity_id'])])
        woreda = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
        main_office = self.env['main.office'].search([('id', '=', vals['main_office'])])
        cell_type = self.env['membership.organization'].search([('id', '=', vals['member_cell_type_id'])])


        if subcity.id != main_office.subcity_id.id:
            raise UserError(_("The Subcity Selected %s is not of Subcity of the Basic Organization %s") % (subcity.name, main_office.subcity_id.name))
        if woreda.id != main_office.wereda_id.id:
            raise UserError(_("The Woreda Selected %s is not of Woreda of the Basic Organization %s") % (woreda.name, main_office.wereda_id.name))
        if cell_type.id != main_office.member_main_type_id.id:
            raise UserError(_("The Type of Organization selected %s is not of The Type of Organization of the Basic Organization %s") % (cell_type.name, main_office.member_main_type_id.name))
        if vals['for_which_members'] != main_office.for_which_members:
            raise UserError(_("The Type selected %s is not of The Type of Basic Organization %s") % (vals['for_which_members'], main_office.for_which_members))
        if vals.get('for_which_members') == 'league' and not vals.get('league_type'):
            raise UserError(_("Please Add League Type for League Main Office %s") % (vals['name_2']))
        if vals.get('for_which_members') == 'league':
            if vals['league_type'] != main_office.league_type:
                raise UserError(_("The Type of League selected %s is not of The Type of League Basic Organization %s") % (vals['league_type'], main_office.league_type))

        naming = ''
        naming_amh = ''

        if vals['for_which_members'] == 'league' and vals['league_type'] == 'young':
            naming = woreda.with_context(lang='en_US').name + '/' + cell_type.with_context(lang='en_US').name + '/Youngster/' + main_office.with_context(lang='en_US').name_2 + '/' + vals['name_2']
            naming_amh = woreda.with_context(lang='am_ET').name + '/' + cell_type.with_context(lang='am_ET').name + '/ወጣት ሊግ/' + main_office.with_context(lang='am_ET').name_2 + '/' + vals['name_2']
        if vals['for_which_members'] == 'league' and vals['league_type'] == 'women':
            naming = woreda.with_context(lang='en_US').name + '/' + cell_type.with_context(lang='en_US').name + '/Woman/' + main_office.with_context(lang='en_US').name_2 + '/' + vals['name_2']
            naming_amh = woreda.with_context(lang='am_ET').name + '/' + cell_type.with_context(lang='am_ET').name + '/ሴት ሊግ/' + main_office.with_context(lang='am_ET').name_2 + '/' + vals['name_2']
        if vals['for_which_members'] == 'member':
            naming = woreda.with_context(lang='en_US').name + '/' + cell_type.with_context(lang='en_US').name + '/Member/' + main_office.with_context(lang='en_US').name_2 + '/' + vals['name_2']
            naming_amh = woreda.with_context(lang='am_ET').name + '/' + cell_type.with_context(lang='am_ET').name + '/አባል/' + main_office.with_context(lang='am_ET').name_2 + '/' + vals['name_2']


        current_lang = self.env.context.get('lang')
        if current_lang == 'am_ET':
            test =self.env['member.cells'].with_context(lang='am_ET').search([('name', '=', naming_amh)])
            if test:
                raise UserError(_("A Cell With This Name Already Exists %s") %  (vals['name_2']))
        if current_lang == 'en_US':
            test =self.env['member.cells'].with_context(lang='en_US').search([('name', '=', naming)])
            if test:
                raise UserError(_("A Cell With This Name Already Exists %s") %  (vals['name_2']))

        res = super(Cells, self).create(vals)

        res.saved = True
        if res.for_which_members == 'league':
            for record in res:
                cell = res.with_context().copy({
                    'name': '/Member/' + res.name_2,
                    'for_which_members': 'member',
                    'duplicate': True,
                    'cell_id': res.id,
                    'main_office': res.main_office.main_office_id.id,
                    'main_office_mixed': res.main_office_mixed.main_office_id.id,
                })
                res.cell_id = cell.id

        name = res.name_2
        if res.for_which_members == 'league' and res.league_type == 'young':
            res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_cell_type_id.with_context(lang='en_US').name + '/Youngster/' +res.main_office.with_context(lang='en_US').name_2 + '/' + name
            res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_cell_type_id.with_context(lang='am_ET').name + '/ወጣት ሊግ/' + res.main_office.with_context(lang='am_ET').name_2 + '/' + name
        if res.for_which_members == 'league' and res.league_type == 'women':
            res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_cell_type_id.with_context(lang='en_US').name + '/Woman/' + res.main_office.with_context(lang='en_US').name_2 + '/' + name
            res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_cell_type_id.with_context(lang='am_ET').name + '/ሴት ሊግ/' + res.main_office.with_context(lang='am_ET').name_2 + '/' + name
        if res.for_which_members == 'member' and not res.duplicate:
            res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_cell_type_id.with_context(lang='en_US').name + '/Member/' + res.main_office.with_context(lang='en_US').name_2 + '/' + name
            res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/' + res.main_office.with_context(lang='am_ET').name_2 + '/' + name
        if res.for_which_members == 'member' and res.duplicate:
            if res.league_type == 'young':
                res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_cell_type_id.with_context(lang='en_US').name + '/Member/Youngster/' + res.main_office.with_context(lang='en_US').name_2 + '/' + name
                res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/ወጣት ሊግ/' + res.main_office.with_context(lang='am_ET').name_2 + '/' + name
            if res.league_type == 'women':
                res.with_context(lang='en_US').name = res.wereda_id.with_context(lang='en_US').name + '/' + res.member_cell_type_id.with_context(lang='en_US').name + '/Member/Youngster/' + res.main_office.with_context(lang='en_US').name_2 + '/' +name
                res.with_context(lang='am_ET').name = res.wereda_id.with_context(lang='am_ET').name + '/' + res.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/ሴት ሊግ/' + res.main_office.with_context(lang='am_ET').name_2 + '/' + name


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


    @api.onchange('name_2', 'subcity_id', 'wereda_id', 'for_which_members', 'member_cell_type_id', 'league_type', 'main_office')
    def _change_name(self):
        """This function will change name"""
        for record in self:
            if record.name_2 and record.subcity_id and record.wereda_id and record.member_cell_type_id and record.main_office:
                wereda = record.with_context(lang='am_ET').wereda_id.name
                main_type = record.with_context(lang='am_ET').member_cell_type_id.name
                main_office = record.with_context(lang='am_ET').main_office.name_2
                name = record.name_2
                if record.for_which_members == 'league' and record.league_type == 'young':
                    record.cell_id.write({
                        'subcity_id': record.subcity_id.id,
                        'wereda_id': record.wereda_id.id,
                        'for_which_members': record.for_which_members,
                        'member_cell_type_id': record.member_cell_type_id.id,
                    })
                    record.cell_id.with_context(lang='am_ET').name =  record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2
                    record.cell_id.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Member/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                    record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Youngster/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                    record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/ወጣት ሊግ/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2
                if record.for_which_members == 'league' and record.league_type == 'women':
                    record.cell_id.write({
                        'subcity_id': record.subcity_id.id,
                        'wereda_id': record.wereda_id.id,
                        'for_which_members': record.for_which_members,
                        'member_cell_type_id': record.member_cell_type_id.id,
                    })
                    record.cell_id.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2
                    record.cell_id.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Member/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                    record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Woman/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                    record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/ሴት ሊግ/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2
                if record.for_which_members == 'member' and not record.duplicate:
                    record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2
                    record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Member/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                if record.for_which_members == 'member' and record.duplicate:
                    if record.league_type == 'young':
                        record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Member/Youngster/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                        record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/ወጣት ሊግ/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2
                    if record.league_type == 'women':
                        record.with_context(lang='en_US').name = record.wereda_id.with_context(lang='en_US').name + '/' + record.member_cell_type_id.with_context(lang='en_US').name + '/Member/Youngster/' + record.main_office.with_context(lang='en_US').name_2 + '/' + record.name_2
                        record.with_context(lang='am_ET').name = record.wereda_id.with_context(lang='am_ET').name + '/' + record.member_cell_type_id.with_context(lang='am_ET').name + '/አባል/ሴት ሊግ/' + record.main_office.with_context(lang='am_ET').name_2 + '/' + record.name_2

                record.saved = True


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
                    if user.has_group('member_minor_configuration.member_group_cell_manager') and not user.has_group('member_minor_configuration.member_group_main_manager'):
                        if record.cell_admin:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_admin = user.id
                    if user.has_group('member_minor_configuration.member_group_finance') and not user.has_group('member_minor_configuration.member_group_main_finance'):
                        if record.cell_finance:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_finance = user.id
                    if user.has_group('member_minor_configuration.member_group_assembler') and not user.has_group('member_minor_configuration.member_group_main_assembler'):
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
                    if user.has_group('member_minor_configuration.member_group_cell_manager') and not user.has_group('member_minor_configuration.member_group_main_manager'):
                        if record.cell_admin:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_admin = user.id
                    if user.has_group('member_minor_configuration.member_group_finance') and not user.has_group('member_minor_configuration.member_group_main_finance'):
                        if record.cell_finance:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_finance = user.id
                    if user.has_group('member_minor_configuration.member_group_assembler') and not user.has_group('member_minor_configuration.member_group_main_assembler'):
                        if record.cell_assembler:
                            pass
                            # raise UserError(_("This Cell Already Has an Administrator. Please request Transfer for this Member before Proceeding"))
                        else:
                            record.cell_assembler = user.id
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


    def update_name(self):
        """This function will update name of cell"""
        for record in self:
            record.saved = False