"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class MainOfficeMembersConfiguration(models.Model):
    _name = "cell.configuration"
    _description = "This model will handle the configuration of member amount in main office"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    for_members_or_leagues = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True)
    minimum_number = fields.Integer(required=True, track_visibility='onchange')
    maximum_number = fields.Integer(required=True, track_visibility='onchange')
    reject = fields.Boolean(default=False, track_visibility='onchange')

class CellMembersConfiguration(models.Model):
    _name = "main.office.configuration"
    _description = "This model will handle the configuration of member amount in cells"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    for_members_or_leagues = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True)
    maximum_cell = fields.Integer(required=True, track_visibility='onchange')
    reject = fields.Boolean(default=False, track_visibility='onchange')    

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
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity, domain="[('branch_ids.branch_manager', '=', user_id)]", track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange')
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
    leader_ids = fields.Many2many('res.partner', 'leader_main_rel', copy=False, domain="['&', '&', '&', '&', ('member_responsibility', '=', 3), ('membership_org','=', member_main_type_id), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", track_visibility='onchange')
    league_leader_ids = fields.Many2many('res.partner', 'league_leader_rel', domain="['&', '&', '&', '&', ('league_org','=', league_main_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False), ('league_status', '=', 'league leader')]", copy=False, track_visibility='onchange')
    total_membership_fee = fields.Float(compute="_all_members_main_office_fee", store=True)
    total_leagues_fee = fields.Float(compute="_all_members_main_office_fee", store=True)
    cells = fields.Boolean(default=False)
    date_of_meeting_eachother = fields.Date()
    place_of_meeting_eachother = fields.Char(translate=True)
    time_of_meeting_eachother = fields.Float()
    date_of_meeting_cells = fields.Date()
    place_of_meeting_cells = fields.Char(translate=True)
    time_of_meeting_cells = fields.Float()
    meeting_memebers_every = fields.Integer()  


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
            record.total_member = len(record.cell_ids.leaders_ids.ids) + len(record.cell_ids.members_ids.ids)
            if record.cell_ids.leaders_ids:
                for leader in record.cell_ids.leaders_ids:
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            if record.cell_ids.members_ids:
                for member in record.cell_ids.members_ids:
                    total += (member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent)
            record.total_member_fee = total

    @api.depends('league_cell_ids.leagues_ids', 'league_cell_ids.league_leaders_ids')
    def _assign_to_main_office_league(self):
        """This function will assign leaders to total members and total fee"""
        for record in self:
            total = 0.00
            record.total_league = len(record.league_cell_ids.leagues_ids.ids) + len(record.league_cell_ids.league_leaders_ids.ids)
            if record.league_cell_ids.leagues_ids:
                for league in record.league_cell_ids.leagues_ids:
                    total += (league.league_payment)
            if record.league_cell_ids.league_leaders_ids:
                for leader in record.league_cell_ids.league_leaders_ids:
                    total += (leader.league_payment)
            record.total_league_fee = total 


    @api.depends('total_member', 'total_league', 'leader_ids', 'league_leader_ids')
    def _all_members_main(self):
        """Collect all in one"""
        for record in self:
            if record.cell_ids:
                record.total_members = record.total_member + len(record.leader_ids.ids)
            if record.league_cell_ids:
                record.total_leagues = record.total_league + len(record.league_leader_ids.ids)


    @api.depends('total_member_fee', 'total_league_fee', 'leader_ids', 'league_leader_ids')
    def _all_members_main_office_fee(self):
        """This function will handle all fees"""
        for record in self:
            if record.cell_ids:
                total = 0.00
                for leader in record.leader_ids:
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
                record.total_membership_fee = record.total_member_fee + total
            if record.league_cell_ids:
                total = 0.00
                for leader in record.league_leader_ids:
                    total += (leader.league_payment)
                record.total_leagues_fee = record.total_league_fee + total


    @api.depends('league_cell_ids')
    def _calculate_league_cells(self):
        """This function will calculate the total cells of main_office"""
        for record in self:
            record.total_cell_league = len(record.league_cell_ids.ids)
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
            if record.total_cell > 0:
                record.cells = True
            else:
                record.cells = False
                record.total_members = 0
                record.total_member_fee = 0.00
                record.total_member = 0
                record.total_membership_fee = 0.00


class Cells(models.Model):
    _name="member.cells"
    _description="This model will contain the cells members will belong in"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(required=True, translate=True, track_visibility='onchange')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity, domain="[('branch_ids.branch_manager', '=', user_id)]", track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    for_which_members = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, track_visibility='onchange')
    member_cell_type_id = fields.Many2one('membership.organization', track_visibility='onchange')
    league_cell_type_id = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange')
    main_office = fields.Many2one('main.office', domain="['&', ('member_main_type_id','=', member_cell_type_id), ('wereda_id', '=', wereda_id)]", track_visibility='onchange')
    main_office_league = fields.Many2one('main.office', domain="['&', ('league_main_type_id', '=', league_cell_type_id), ('wereda_id', '=', wereda_id)]", track_visibility='onchange')
    members_ids = fields.Many2many('res.partner', domain="['&', '&', '&', ('membership_org','=', member_cell_type_id), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), '|', ('is_member', '=', True), ('is_leader', '=', True)]", track_visibility='onchange')
    date_of_meeting = fields.Date()
    place_of_meeting = fields.Char(translate=True)
    time_of_meeting = fields.Float()
    total = fields.Integer(store=True)
    leaders_ids = fields.Many2many('res.partner', 'leader_cell_rel', domain="['&', '&', '&', '&', ('member_responsibility', '=', 2), ('membership_org','=', member_cell_type_id), ('is_member', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False)]", string="Leaders", track_visibility='onchange')
    league_leaders_ids = fields.Many2many('res.partner', 'league_leader_cell_rel', domain="['&', '&', '&', '&', ('league_org','=', league_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False), ('league_status', '=', 'league leader')]", string="League Leaders", track_visibility='onchange')
    leagues_ids = fields.Many2many('res.partner', 'league_cell_rel', domain="['&', '&', '&', '&', ('league_org','=', league_cell_type_id), ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('league_member_cells', '=', False), ('league_status', '=', 'league member')]", string="League Members", track_visibility='onchange')
    all_partners = fields.Many2many('res.partner', 'all_partner_rel', store=True)
    total_members = fields.Integer(compute="_calculate_total_members", store=True)
    total_leaders = fields.Integer(compute="_assign_leaders_cells", store=True)
    total_leagues = fields.Integer(compute="_calculate_total_leagues", store=True)
    total_leader_leagues = fields.Integer(compute="_calculate_total_leader_leagues", store=True)
    total_leader_fee = fields.Float(store=True)
    total_member_fee = fields.Float(store=True)
    total_league_fee = fields.Float(store=True)
    total_leader_league_fee = fields.Float(store=True)
    total_membership_fee = fields.Float(compute="_compute_totals", store=True)
    total = fields.Integer(compute="_all_members", store=True)
    members = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        """This function will check if the numbers added are what is estimated"""
        rec = super(Cells, self).create(vals)
        user = self.env.user
        config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', rec.for_which_members)])
        if rec.total < config.minimum_number:
            warning_message = "The Added Numbers Of Members Is " + str(rec.total) + " Which Is Less Than " + str(config.minimum_number) + " According To The Rule Given."
            if config.reject:
                raise UserError(_(warning_message))
            else:
                user.notify_warning(warning_message, '<h4>Minimum Number of Members not Reached.</h4>', True)
        elif rec.total > config.maximum_number:
            if config.reject:
                message="The Added Numbers Of Members Is " + str(rec.total) + " Which Is More Than " + str(config.maximum_number) + " According To The Rule Given."
                raise UserError(_(message))
            else:
                message = "The Number Of Members You Added Is Going To Exceed The Maximum Number Given In The Rule."
                user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True)   
        return rec       

    # def write(self, vals):
    #     """This function will check if members are removed"""
    #     new = vals['members_ids'][0][2]
    #     for record in self:
    #         before = record.members_ids.ids
    #         all_members = False
    #         for ids in before:
    #             if ids not in new:
    #                 all_members = True
    #             break
    #         if all_members:
    #             for ids in before:
    #                 if ids not in new:
    #                     partner = self.env['res.partner'].search([('id', '=', ids)])
    #                     if record.for_which_members == 'member':
    #                         partner.main_office = False
    #                         partner.member_cells = False
    #                     if record.for_which_members == 'league':
    #                         partner.league_main_office = False
    #                         partner.league_member_cells = False

    #     return super(Cells, self).write(vals)


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
            user = self.env.user
            total_cells = len(record.main_office.cell_ids.ids)
            config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
            if total_cells >= config.maximum_cell:
                if config.reject:
                    message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                    raise ValidationError(_(message))
                else:
                    message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                    user.notify_warning(message, '<h4>Maximum Numbers Of Cells Are Exceeding.</h4>', True)

    @api.onchange('main_office_league')
    def _can_not_add_to_main_office(self):
        """This will check if excess cells are in main office"""
        for record in self:
            user = self.env.user
            total_cells = len(record.main_office_league.league_cell_ids.ids)
            config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
            if total_cells >= config.maximum_cell:
                if config.reject:
                    message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                    raise ValidationError(_(message))
                else:
                    message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                    user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True)    

    @api.onchange('main_office', 'main_office_league')
    def _pick_a_organization(self):
        """This function will make usre an organization is picked before main office"""
        for record in self:
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
                for leader in record.leaders_ids:
                    leader.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            record.total_leader_fee = total

    @api.depends('members_ids')
    def _calculate_total_members(self):
        """This function will calculate the total members"""
        for record in self:
            total = 0.00
            record.total_members = len(record.members_ids.ids)
            if record.members_ids:
                for memb in record.members_ids:
                    memb.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (memb.membership_monthly_fee_cash + memb.membership_monthly_fee_cash_from_percent)
            record.total_member_fee = total

    @api.depends('leagues_ids')
    def _calculate_total_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leagues = len(record.leagues_ids.ids)
            if record.leagues_ids:
                for league in record.leagues_ids:
                    league.write({
                        'league_main_office': record.main_office_league.id,
                        'league_member_cells': record.id
                    })
                    total += (league.league_payment)
            record.total_league_fee = total        


    @api.depends('league_leaders_ids')
    def _calculate_total_leader_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leader_leagues = len(record.league_leaders_ids.ids)
            if record.league_leaders_ids:
                for league in record.league_leaders_ids:
                    league.write({
                        'league_main_office': record.main_office_league.id,
                        'league_member_cells': record.id
                    })
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
                # if record.total_members == 0 and record.total_leaders == 0:
                #     record.members = False
                #     record.total_membership_fee = 0.00
                #     record.total_leagues = 0
                #     record.total_leader_leagues = 0


    @api.depends('total_leader_fee', 'total_member_fee', 'total_league_fee', 'total_leader_league_fee')
    def _compute_totals(self):
        """This function will compute the total fee and total members"""
        for record in self:
            if record.total_member_fee or record.total_leader_fee or record.total_league_fee or record.total_leader_league_fee:
                record.total_membership_fee = record.total_leader_fee + record.total_member_fee + record.total_league_fee + record.total_leader_league_fee