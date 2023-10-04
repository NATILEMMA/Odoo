"""This file will deal with the modification of the membership payment"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import os
import re
from odoo.tools import config
import base64
import hashlib
import logging

original = 0.00

_logger = logging.getLogger(__name__)
             

class LeaguePayment(models.Model):
    _name="each.league.payment"
    _description="This model will handle each league's payments"
    _order = "month"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    members_payment_id = fields.Many2one('membership.payment', copy=False, track_visibility='onchange')
    cell_payment_id = fields.Many2one('membership.cell.payment', copy=False)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one(related='cell_payment_id.subcity_id', readonly=True, store=True)
    wereda_id = fields.Many2one(related='cell_payment_id.wereda_id', readonly=True, store=True, track_visibility='onchange')
    league_id = fields.Many2one('res.partner', domain="[('league_member_cells', '=', cell_payment_id)]", copy=False)
    amount_paid = fields.Float(store=True, default=0.00, track_visibility='onchange')
    amount_remaining = fields.Float(store=True, compute="_compute_remaining_for_league")
    fee_amount = fields.Float(store=True, compute="_get_from_league")
    state = fields.Selection(selection=[('paid', 'Paid'), ('paid some', 'Paid Some'), ('not payed', 'Not Payed')], track_visibility='onchange', store=True)
    traced_league_payment = fields.Float(string="Tracked Payment", store=True)
    year = fields.Many2one(related="month.fiscal_year", string='Year', store=True, track_visibility='onchange')
    month = fields.Many2one('reconciliation.time.fream', domain="[('is_active', '=', True)]", string="Payment Month", store=True, track_visibility='onchange')
    annual_league_fee = fields.Float()
    original = fields.Float()
    id_payment = fields.Float(track_visibility='onchange')
    paid_for_id = fields.Boolean(default=False, track_visibility='onchange')
    paid = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        """This function will create a league payment and delete an exisitng one"""
        month = self.env['reconciliation.time.fream'].search([('id', '=', vals['month']), ('is_active', '=', True)])
        payment = self.env['each.league.payment'].search([('month', '=', vals['month']), ('year', '=', month.fiscal_year.id), ('league_id', '=', vals['league_id'])])
        if payment:
            payment.write({
                'state': 'paid'
            })
            return payment
        else:
            return super(LeaguePayment, self).create(vals)

    @api.depends('amount_paid')
    def _compute_remaining_for_league(self):
        """This function will compute the remaining amount"""
        for record in self:
            if (record.amount_paid > 0.00) and (record.annual_league_fee >= record.amount_paid): 
                if (record.amount_paid >= record.fee_amount):
                    record.write({
                        'amount_remaining': 0.00,
                        'state': 'paid'
                    })
                else:
                    record.write({
                        'amount_remaining': record.fee_amount - record.amount_paid,
                        'state': 'paid some'
                    })


    @api.depends('league_id')
    def _get_from_league(self):
        """This will get the membership fee from league"""
        for record in self:
            if record.league_id:
                record.fee_amount = record.league_id.league_payment
                record.annual_league_fee = 12 * record.fee_amount


    def print_league_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_features.create_league_payment_report').report_action(record._origin.id)

    def add_attachment(self):
        """this function will add attachments"""
        view_id = self.env.ref('members_features.each_league_payment_form').id
        context = self._context.copy()
        return {
            'name':'Payment',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'each.league.payment',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'res_id':self.id,
            'target':'current',
            'context':context,
        }

    def get_dashboard_url(self):
        """This function will get url"""
        return "/my/payment_details/%s/%s" % (self.id, self.cell_payment_id.payment_for_league_member)



class MembershipPayment(models.Model):
    _name="each.member.payment"
    _description="This model will handle each member's payment"
    _order = "month"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    members_payment_id = fields.Many2one('membership.payment', copy=False)
    cell_payment_id = fields.Many2one('membership.cell.payment', copy=False)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one(related='cell_payment_id.subcity_id', readonly=True, store=True)
    wereda_id = fields.Many2one(related='cell_payment_id.wereda_id', readonly=True, store=True)
    member_id = fields.Many2one('res.partner',  domain="[('member_cells', '=', cell_payment_id)]", copy=False, track_visibility='onchange')
    amount_paid = fields.Float(store=True, default=0.00, track_visibility='onchange')
    amount_remaining = fields.Float(store=True, compute="_compute_remaining")
    fee_amount = fields.Float(store=True, compute="_get_from_member")
    traced_member_payment = fields.Float(string="Tracked Payment", store=True)
    state = fields.Selection(selection=[('paid', 'Paid'), ('paid some', 'Paid Some'), ('not payed', 'Not Payed')], track_visibility='onchange', store=True)
    year = fields.Many2one(related="month.fiscal_year", string='Year', store=True, track_visibility='onchange')
    month = fields.Many2one('reconciliation.time.fream', domain="[('is_active', '=', True)]", string="Payment Month", store=True, track_visibility='onchange')
    annual_fee = fields.Float()
    original = fields.Float()
    id_payment = fields.Float(track_visibility='onchange')
    paid_for_id = fields.Boolean(default=False, track_visibility='onchange')
    paid = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        """This function will create a member payment and delete an exisitng one"""
        month = self.env['reconciliation.time.fream'].search([('id', '=', vals['month']), ('is_active', '=', True)])
        payment = self.env['each.member.payment'].search([('month', '=', vals['month']), ('year', '=', month.fiscal_year.id), ('member_id', '=', vals['member_id'])])
        if payment:
            payment.write({
                'state': 'paid'
            })
            return payment
        else:
            return super(MembershipPayment, self).create(vals)

    @api.depends('amount_paid')
    def _compute_remaining(self):
        """This function will compute the remaining amount"""
        for record in self:           
            if (record.amount_paid > 0.00) and (record.annual_fee >= record.amount_paid):
                if (record.amount_paid >= record.fee_amount):
                    record.write({
                        'amount_remaining': 0.00,
                        'state': 'paid'
                    })                 
                else:                   
                    record.write({
                        'amount_remaining': record.fee_amount - record.amount_paid,
                        'state': 'paid some'
                    })


    @api.depends('member_id')
    def _get_from_member(self):
        """This will get the membership fee from member"""
        for record in self:
            if record.member_id:
                record.fee_amount = record.member_id.membership_monthly_fee_cash_from_percent + record.member_id.membership_monthly_fee_cash
                record.annual_fee = 12 * (record.member_id.membership_monthly_fee_cash_from_percent + record.member_id.membership_monthly_fee_cash)

    def print_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_features.create_member_payment_report').report_action(record._origin.id)

    def add_attachment(self):
        """this function will add attachments"""
        view_id = self.env.ref('members_features.each_member_payment_form').id
        context = self._context.copy()
        return {
            'name':'Payment',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'each.member.payment',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'res_id':self.id,
            'target':'current',
            'context':context,
        }

    def get_dashboard_url(self):
        """This function will get url"""
        return "/my/payment_details/%s/%s" % (self.id, self.cell_payment_id.payment_for_league_member)



class ProductsToDonate(models.Model):
    _name = "product.to.donate"
    _description = "This model will have a list of products that are donated"

    product_id = fields.Many2one('product.product', required=True)
    cost = fields.Float(required=True, store=True)
    amount = fields.Integer(required=True)
    donor_payment_id = fields.Many2one('donation.payment')


class DonationPayments(models.Model):
    _name = "donation.payment"
    _description = "This model will create donation payments"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    year = fields.Many2one("fiscal.year", string='Year', store=True, track_visibility='onchange', required=True)
    month = fields.Many2one('reconciliation.time.fream', domain="[('fiscal_year', '=', year), ('is_active', '=', True)]", string="Payment Month", track_visibility='onchange', required=True)
    amount = fields.Float(string="Amount Received", track_visibility='onchange', required=True, store=True)
    payment_for = fields.Selection(selection=[('city', 'City'), ('subcity', 'Sub City'), ('wereda', 'Woreda')], default='city', required=True)
    city = fields.Many2one('membership.city.handlers')
    subcity_id = fields.Many2one('membership.handlers.parent', domain="[('city_id', '=', city)]", track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", string="Basic Organization")
    member_cell = fields.Many2one('member.cells', domain="['|', ('main_office', '=', main_office), ('main_office', '=', main_office)]", string="Cell")
    product_cash = fields.Selection(selection=[('product', 'Product'), ('cash', 'Cash')], default='cash', string="Product or Cash")
    product_ids = fields.One2many('product.to.donate', 'donor_payment_id')
    for_donor_or_supporter = fields.Selection(selection=[('donor', 'Donor'), ('supporter', 'Supporter')], required=True, default="supporter", string="Donor or Supporter")
    reason = fields.Text(translate=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('submit', 'Submit'), ('registered', 'Registered')], default="draft")
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    cell_payment = fields.Many2one('membership.cell.payment')
    main_payment = fields.Many2one('membership.payment')


    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('donation.payment')
        return super(DonationPayments, self).create(vals)


    def unlink(self):
        """This function will only delete payments in draft state"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You Can Only Delete Those Payments That Are In Draft State."))
        return super(DonationPayments, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state == 'submit' or record.state == 'registered':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    @api.onchange('subcity_id')
    def _chnage_subcity_error(self):
        """This function will make sure required fields are field before seelction of another"""
        for record in self:
            if record.subcity_id:
                record.wereda_id = False
                record.main_office = False
                record.member_cell = False
                if not record.city:
                    raise UserError(_("Please Fill In City Information First!"))


    @api.onchange('wereda_id')
    def _chnage_wereda_error(self):
        """This function will make sure required fields are field before seelction of another"""
        for record in self:
            if record.wereda_id:
                record.main_office = False
                record.member_cell = False
                if not record.city or not record.subcity_id:
                    raise UserError(_("Please Fill In City and Sub City Information First!"))

    @api.onchange('main_office')
    def _chnage_wereda_error(self):
        """This function will make sure required fields are field before seelction of another"""
        for record in self:
            if record.main_office:
                record.member_cell = False
                if not record.city or not record.subcity_id or not record.wereda_id:
                    raise UserError(_("Please Fill In City, Sub City and Woreda Information First!"))

    @api.onchange('member_cell')
    def _chnage_wereda_error(self):
        """This function will make sure required fields are field before seelction of another"""
        for record in self:
            if record.member_cell:
                if not record.city or not record.subcity_id or not record.wereda_id or not record.main_office:
                    raise UserError(_("Please Fill In City, Sub City, Woreda and Main Office Information First!"))

    @api.onchange('product_ids')
    def _get_amoun(self):
        """This function will calculate the amount of product in cash"""
        for record in self:
            if record.product_cash == 'product' and record.product_ids:
                total = 0
                for product in record.product_ids:
                    total += (product.cost * product.amount)
                record.amount = total


    @api.onchange('product_cash')
    def _make_balues_null(self):
        """This function will make fields null"""
        for record in self:
            if record.product_cash == 'product':
                record.amount = 0.00
            if record.product_cash == 'cash':
                record.product_ids = [(5, 0, 0)]
                record.amount = 0.00


    def submit_button(self):
        """This function will submit payment"""
        for record in self:
            for product in record.product_ids:
                if product.amount == 0 or product.cost == 0.00:
                    raise UserError(_("Please Add The Amount and Cost of the Product"))
            if record.amount == 0.00:
                raise UserError(_("Please Add The Amount of Donation"))
            if not record.reason:
                raise UserError(_("Please Add A Reason For Your Donation"))
            record.state = 'submit'

    def draft_button(self):
        """This function will reverse payment back to draft"""
        for record in self:
            record.state = 'draft'

    def print_donor_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_features.create_donor_payment_report').report_action(record._origin.id)



class CellPayment(models.Model):
    _name="membership.cell.payment"
    _description="This model will handle with the payment of cells"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_cell_member(self):
        """This function will set default value for cell"""
        return self.env['member.cells'].search([('cell_finance', '=', self.env.user.id), ('state', '=', 'active')], limit=1).id

    def _default_main_office(self):
        """This function will set default value for cell"""
        return self.env['member.cells'].search([('cell_finance', '=', self.env.user.id), ('state', '=', 'active')], limit=1).main_office.id      

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['member.cells'].search([('cell_finance', '=', self.env.user.id), ('state', '=', 'active')], limit=1).wereda_id.id  

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['member.cells'].search([('cell_finance', '=', self.env.user.id), ('state', '=', 'active')], limit=1).subcity_id.id   


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    year = fields.Many2one("fiscal.year", string='Year', store=True, track_visibility='onchange', required=True)
    month = fields.Many2one('reconciliation.time.fream', domain="[('fiscal_year', '=', year), ('is_active', '=', True)]", string="Payment Month", track_visibility='onchange', required=True)
    amount = fields.Float(string="Amount Received", track_visibility='onchange', required=True)
    main_office_payment = fields.Many2one('membership.payment')
    estimated_amount_remaining = fields.Float(string="Amount Remaining", readonly=True, store=True)
    total_estimated = fields.Float(compute="_get_total", string="Total Estimated", store=True, readonly=True)
    total_paid = fields.Float(compute="_get_paid_total", string="Total Paid", store=True, readonly=True)
    total_remaining = fields.Float(compute="_get_total", string="Total remaining", store=True, readonly=True)
    subcity_id = fields.Many2one('membership.handlers.parent', default=_default_subcity, track_visibility='onchange', required=True)
    wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange', required=True)
    payment_for_league_member = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True, string="League or Member")
    main_office = fields.Many2one('main.office', string="Basic Organization",  default=_default_main_office, domain="['&', ('for_which_members', '=', payment_for_league_member), ('wereda_id', '=', wereda_id)]", required=True, copy=False, track_visibility='onchange')
    member_cell = fields.Many2one('member.cells', string="Member Cell", default=_default_cell_member, domain="[('main_office', '=', main_office), ('state', '=', 'active')]", required=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('pending payments', 'Pending Payments'), ('submit', 'Submit'), ('registered', 'Registered')], default="draft")
    member_ids = fields.One2many('each.member.payment', 'cell_payment_id', copy=False, track_visibility='onchange')
    total_estimated_for_members = fields.Float(compute="_compute_members_fees", string="Members' Estimated", store=True)
    total_paid_for_members = fields.Float(compute="_compute_members_fees", string="Members' Paid", store=True)
    total_remaining_for_members = fields.Float(compute="_compute_members_fees", string="Members' Remaining", store=True)
    total_id_payments_members = fields.Float(compute="_compute_members_fees", string="Members' ID Payment", store=True)
    league_ids = fields.One2many('each.league.payment', 'cell_payment_id', copy=False, track_visibility='onchange')
    total_estimated_for_leagues = fields.Float(compute="_compute_leagues_fees", string="Leagues' Estimated", store=True)
    total_paid_for_leagues = fields.Float(compute="_get_paid_total", string="Leagues' Paid", store=True)
    total_remaining_for_leagues = fields.Float(compute="_compute_leagues_fees", string="Leagues' Remaining", store=True)
    total_id_payments_leagues = fields.Float(compute="_compute_leagues_fees", string="Leagues' ID Payment", store=True)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    

    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('membership.payment')
        if vals['member_cell'] and vals['payment_for_league_member'] == 'member':
            member_cell = self.env['member.cells'].search([('id', '=', vals['member_cell'])]).members_ids.ids
            leader_cell = self.env['member.cells'].search([('id', '=', vals['member_cell'])]).leaders_ids.ids
            if len(member_cell) == 0 and len(leader_cell) == 0:
                raise UserError(_("You Can Not Create Payment For A Cell That Has No Members"))
        if vals['member_cell'] and vals['payment_for_league_member'] == 'league':
            league_cell = self.env['member.cells'].search([('id', '=', vals['member_cell'])]).leagues_ids.ids
            league_leader_cell = self.env['member.cells'].search([('id', '=', vals['member_cell'])]).league_leaders_ids.ids
            if len(league_cell) == 0 and len(league_leader_cell) == 0:
                raise UserError(_("You Can Not Create Payment For A Cell That Has No Leagues"))
        if vals['main_office']:
            main_office_cell = self.env['main.office'].search([('id', '=', vals['main_office'])]).cell_ids.ids
            if len(main_office_cell) == 0:
                raise UserError(_("You Can Not Create Payment For A Basic Organization That Has No Cells"))
        if vals['payment_for_league_member'] == 'member' or vals['payment_for_league_member'] == 'league':
            all_payments = self.env['membership.cell.payment'].search([('year', '=', vals['year']), ('month', '=', vals['month']), ('member_cell', '=', vals['member_cell'])])
            if all_payments:
                raise UserError(_("Payment for your Cell for this Month Already Exists"))
        return super(CellPayment, self).create(vals)


    def unlink(self):
        """This function will only delete payments that are in draft state"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You Can Only Delete Those Payments That Are In Draft State."))
        return super(CellPayment, self).unlink()

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state == 'submit' or record.state == 'registered':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    @api.depends('member_ids', 'amount')
    def _compute_members_fees(self):
        """This function will computethe fees for members"""
        for record in self:
            if record.member_ids:
                record.total_estimated_for_members = sum(record.member_ids.mapped('fee_amount'))
                record.total_remaining_for_members = sum(record.member_ids.mapped('amount_remaining'))
                record.total_id_payments_members = sum(record.member_ids.mapped('id_payment'))
                record.total_paid_for_members = sum(record.member_ids.mapped('amount_paid'))
                record.estimated_amount_remaining = record.amount - (record.total_paid_for_members + record.total_id_payments_members)

    @api.depends('league_ids', 'amount')
    def _compute_leagues_fees(self):
        """This function will computethe fees for members"""
        for record in self:
            if record.league_ids:
                record.total_estimated_for_leagues = sum(record.league_ids.mapped('fee_amount'))
                record.total_remaining_for_leagues = sum(record.league_ids.mapped('amount_remaining'))                
                record.total_id_payments_leagues = sum(record.league_ids.mapped('id_payment'))
                record.total_paid_for_leagues = sum(record.league_ids.mapped('amount_paid'))
                record.estimated_amount_remaining = record.amount - (record.total_paid_for_leagues + record.total_id_payments_leagues)



    @api.onchange('subcity_id')
    def _change_subcity(self):
        """This function will make false"""
        for record in self:
            if record.subcity_id:
                # if record.subcity_id.id != record.wereda_id.parent_id.id:
                record.wereda_id = False
                record.main_office = False
                record.member_cell = False

    @api.onchange('wereda_id')
    def _change_woreda(self):
        """This function will make false"""
        for record in self:
            if record.wereda_id:
                record.main_office = False
                record.member_cell = False
                if not record.subcity_id:
                    raise UserError(_("Please Fill In The Sub City Information First!"))


    @api.onchange('main_office')
    def _change_main_office(self):
        """This function will make false"""
        for record in self:
            if record.main_office:
                record.member_cell = False
                if not record.wereda_id or not record.subcity_id:
                    raise UserError(_("Please Fill In The Woreda and Sub City Information First!"))

    @api.onchange('member_cell')
    def _chnage_member_cell(self):
        """This function will first check"""
        for record in self:
            if record.member_cell:
                if not record.main_office or not record.wereda_id or not record.subcity_id:
                    raise UserError(_("Please Fill In The Basic Organization, Woreda and Sub City Information First!"))


    @api.onchange('payment_for_league_member')
    def _change_toggle(self):
        """This function will make false"""
        for record in self:
            if record.payment_for_league_member:
                record.subcity_id = False
                record.wereda_id = False
                record.main_office = False
                record.member_cell = False



class Payment(models.Model):
    _name="membership.payment"
    _description="This model will handle with the payment of memberships"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_main_office(self):
        """This function will set default value for cell"""
        return self.env['main.office'].search([('main_finance', '=', self.env.user.id)], limit=1).id       

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_finance', '=', self.env.user.id)], limit=1).wereda_id.id  

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['main.office'].search([('main_finance', '=', self.env.user.id)], limit=1).subcity_id.id   


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    year = fields.Many2one("fiscal.year", string='Year', store=True, track_visibility='onchange', required=True)
    month = fields.Many2one('reconciliation.time.fream', domain="[('fiscal_year', '=', year), ('is_active', '=', True)]", string="Payment Month", track_visibility='onchange', required=True)
    amount_collected = fields.Float(store=True, compute="_get_totals")
    amount = fields.Float(string="Amount Received", track_visibility='onchange', required=True)
    estimated_amount_remaining = fields.Float(compute="_claculate_remaining", string="Amount Remaining", store=True)
    total_estimated_for_cells = fields.Float(compute="_get_totals", string="Total Estimated of Cells", store=True, readonly=True)
    total_paid_for_cells = fields.Float(compute="_get_totals", string="Total Paid of Cells", store=True, readonly=True)
    total_remaining_for_cells = fields.Float(compute="_get_totals", string="Total remaining of Cells", store=True, readonly=True)
    subcity_id = fields.Many2one('membership.handlers.parent',track_visibility='onchange', default=_default_subcity, required=True)
    wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', subcity_id)]", default=_default_wereda, track_visibility='onchange', required=True)
    payment_for_league_member = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True)
    main_office = fields.Many2one('main.office', default=_default_main_office, domain="['&', ('for_which_members', '=', payment_for_league_member), ('wereda_id', '=', wereda_id)]", copy=False, track_visibility='onchange', required=True, string="Basic Organization")
    state = fields.Selection(selection=[('draft', 'Draft'), ('pending payments', 'Pending Payments'), ('submit', 'Submit'), ('registered', 'Registered')], default="draft")
    cell_payment_ids = fields.One2many('membership.cell.payment', 'main_office_payment')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    total_paid = fields.Float()


    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        all_payments = self.env['membership.payment'].search([('year', '=', vals['year']), ('month', '=', vals['month']), ('main_office', '=', vals['main_office'])])
        if all_payments:
            raise UserError(_("Payment for your Basic Organization for this Month Already Exists"))
        vals['name'] = self.env['ir.sequence'].next_by_code('main.office.payment')
        return super(Payment, self).create(vals)


    def unlink(self):
        """This function will only delete payments that are in draft state"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You Can Only Delete Those Payments That Are In Draft State."))
        return super(Payment, self).unlink()


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state == 'submit' or record.state == 'registered':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    @api.onchange('subcity_id')
    def _change_subcity(self):
        """This function will make false"""
        for record in self:
            if record.subcity_id:
                # if record.subcity_id.id != record.wereda_id.parent_id.id:
                record.wereda_id = False
                record.main_office = False
                record.member_cell = False
                record.league_cell = False

    @api.onchange('wereda_id')
    def _change_woreda(self):
        """This function will make false"""
        for record in self:
            if record.wereda_id:
                record.main_office = False
                record.member_cell = False
                record.league_cell = False
                if not record.subcity_id:
                    raise UserError(_("Please Fill In The Sub City Information First!"))


    @api.onchange('main_office')
    def _change_main_office(self):
        """This function will make false"""
        for record in self:
            if record.main_office:
                record.member_cell = False
                record.league_cell = False
                if not record.wereda_id or not record.subcity_id:
                    raise UserError(_("Please Fill In The Woreda and Sub City Information First!"))

    @api.onchange('payment_for_league_member')
    def _change_toggle(self):
        """This function will make false"""
        for record in self:
            if record.payment_for_league_member:
                record.subcity_id = False
                record.wereda_id = False
                record.main_office = False
                record.member_cell = False
                record.league_cell = False


    @api.depends('amount_collected', 'amount')
    def _claculate_remaining(self):
        for record in self:
            record.estimated_amount_remaining = record.amount - record.amount_collected



    def start_button(self):
        """This will bring all cells under a main office"""
        for record in self:
            cell_payment = self.env['membership.cell.payment'].search([('year', '=', record.year.id), ('month', '=', record.month.id), ('main_office', '=', record.main_office.id), ('state', '=', 'submit')])
            if cell_payment:
                record.cell_payment_ids = cell_payment
            else:
                raise UserError(_("There are No Payments Made By Cells for this Month"))

            if record.payment_for_league_member == 'member':
                record.total_estimated_for_cells = sum(record.cell_payment_ids.member_ids.mapped('fee_amount'))
                record.total_paid_for_cells = sum(record.cell_payment_ids.member_ids.mapped('amount_paid'))
            if record.payment_for_league_member == 'league':
                record.total_estimated_for_cells = sum(record.cell_payment_ids.league_ids.mapped('fee_amount'))
                record.total_paid_for_cells = sum(record.cell_payment_ids.league_ids.mapped('amount_paid'))
            
            record.state = 'pending payments'



    @api.depends('cell_payment_ids')
    def _get_totals(self):
        """This function will get total information from cell payments"""
        for record in self:
            record.total_estimated_for_cells = sum(record.cell_payment_ids.mapped('total_estimated_for_members')) + sum(record.cell_payment_ids.mapped('total_estimated_for_leagues'))
            record.total_paid_for_cells = sum(record.cell_payment_ids.mapped('total_paid_for_members') + record.cell_payment_ids.mapped('total_id_payments_members')) + sum(record.cell_payment_ids.mapped('total_paid_for_leagues') + record.cell_payment_ids.mapped('total_id_payments_leagues'))
            record.total_remaining_for_cells = sum(record.cell_payment_ids.mapped('total_remaining_for_members')) + sum(record.cell_payment_ids.mapped('total_remaining_for_leagues'))
            record.amount_collected = sum(record.cell_payment_ids.mapped('amount'))

    def submit_button(self):
        """This function will make cells registered"""
        for record in self:
            if (record.amount == 0.00):
                raise UserError(_("Please Add The Amount Paid"))
            if record.cell_payment_ids:
                for cell in record.cell_payment_ids:
                    cell.state = 'registered'
            record.state = 'submit'


    def draft_button(self):
        """This function will make sells submitted now"""
        for record in self:
            if record.cell_payment_ids:
                for cell in record.cell_payment_ids:
                    cell.state = 'submit'
                record.cell_payment_ids = [(5, 0, 0)]
            record.state = 'draft'
            