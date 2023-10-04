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
    _inherit="each.league.payment"

    main_office_id = fields.Many2one(related="league_id.league_main_office", readonly=True, store=True)
    cell_id = fields.Many2one(related="league_id.league_member_cells", readonly=True, store=True)
    league_type = fields.Selection(related="league_id.league_type", readonly=True, store=True)
    type_of_payment = fields.Selection(related="league_id.type_of_payment", readonly=True, store=True)



class MembershipPayment(models.Model):
    _inherit="each.member.payment"

    main_office_id = fields.Many2one(related="member_id.main_office", readonly=True, store=True)
    cell_id = fields.Many2one(related="member_id.member_cells", readonly=True, store=True)
    type_of_payment = fields.Selection(related="member_id.type_of_payment", readonly=True, store=True)


class DonationPayments(models.Model):
    _inherit = "donation.payment"

    donor_ids = fields.Many2one('donors')
    supporter_id = fields.Many2one('supporter.members')


class CellPayment(models.Model):
    _inherit="membership.cell.payment"

    def start_button(self):
        """This function will generate payments"""
        for record in self:       

            if record.member_ids:
                for member in record.member_ids:
                    member.unlink()
                record.member_ids = [(5, 0, 0)]
            if record.league_ids:
                for league in record.league_ids:
                    league.unlink()
                record.league_ids = [(5, 0, 0)]

            if record.payment_for_league_member == 'member':
                for member in record.member_cell.members_ids:
                    paid_month = self.env['each.member.payment'].search([('member_id', '=', member.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                    if paid_month.id:
                        paid_month.write({
                            'cell_payment_id': record.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id                       
                        })
                        record.write({
                            'member_ids': [(4, paid_month.id)]
                        })
                    else:    
                        payment = self.env['each.member.payment'].sudo().create({
                            'member_id': member.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id,
                            'fee_amount': member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent,
                            'amount_remaining': member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent,
                            'amount_paid': 0.00,
                            'state': 'not payed',
                            'annual_fee': 12 * (member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent),
                            'traced_member_payment': member.track_member_fee,
                            'year': record.year.id,
                            'month': record.month.id,
                            'cell_payment_id': record.id,
                            'type_of_payment': member.type_of_payment,
                            'id_payment': 0.00
                        })
                        member.write({
                            'membership_payments': [(4, payment.id)],
                            'year_of_payment': payment.year.id
                        })
                for leader in record.member_cell.leaders_ids:
                    paid_month = self.env['each.member.payment'].search([('member_id', '=', leader.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                    if paid_month.id:
                        paid_month.write({
                            'cell_payment_id': record.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id                        
                        })
                        record.write({
                            'member_ids': [(4, paid_month.id)]
                        })
                    else:    
                        payment = self.env['each.member.payment'].sudo().create({
                            'member_id': leader.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id,
                            'fee_amount': leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent,
                            'amount_remaining': leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent,
                            'amount_paid': 0.00,
                            'state': 'not payed',
                            'annual_fee': 12 * (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent),
                            'traced_member_payment': leader.track_member_fee,
                            'year': record.year.id,
                            'month': record.month.id,
                            'cell_payment_id': record.id,
                            'type_of_payment': leader.type_of_payment,
                            'id_payment': 0.00
                        })
                        leader.write({
                            'membership_payments': [(4, payment.id)],
                            'year_of_payment': payment.year.id
                        })
            if record.payment_for_league_member == 'league':

                for league in record.member_cell.leagues_ids:
                    paid_month = self.env['each.league.payment'].search([('league_id', '=', league.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                    if paid_month.id:
                        paid_month.write({
                            'cell_payment_id': record.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id,
                            'league_type': league.league_type,                     
                        })
                        record.write({
                            'league_ids': [(4, paid_month.id)]
                        })
                    else:    
                        payment = self.env['each.league.payment'].sudo().create({
                            'league_id': league.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id,
                            'fee_amount': league.league_payment,
                            'amount_remaining': league.league_payment,
                            'amount_paid': 0.00,
                            'state': 'not payed',
                            'annual_league_fee': 12 * (league.league_payment),
                            'traced_league_payment': league.track_league_fee,
                            'year': record.year.id,
                            'month': record.month.id,
                            'cell_payment_id': record.id,
                            'type_of_payment': league.type_of_payment,
                            'league_type': league.league_type,
                            'id_payment': 0.00
                        })
                        league.write({
                            'league_payments': [(4, payment.id)],
                            'year_of_payment': payment.year.id
                        })
                for league in record.member_cell.league_leaders_ids:
                    paid_month = self.env['each.league.payment'].search([('league_id', '=', league.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                    if paid_month.id:
                        paid_month.write({
                            'cell_payment_id': record.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id,
                            'league_type': league.league_type,                         
                        })
                        record.write({
                            'league_ids': [(4, paid_month.id)]
                        })
                    else:    
                        payment = self.env['each.league.payment'].sudo().create({
                            'league_id': league.id,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'main_office_id': record.main_office.id,
                            'cell_id': record.member_cell.id,
                            'fee_amount': league.league_payment,
                            'amount_remaining': league.league_payment,
                            'amount_paid': 0.00,
                            'state': 'not payed',
                            'annual_league_fee': 12 * (league.league_payment),
                            'traced_league_payment': league.track_league_fee,
                            'year': record.year.id,
                            'month': record.month.id,
                            'cell_payment_id': record.id,
                            'type_of_payment': league.type_of_payment,
                            'league_type': league.league_type,
                            'id_payment': 0.00
                        })
                        league.write({
                            'league_payments': [(4, payment.id)],
                            'year_of_payment': payment.year.id
                        })  
            record.state = 'pending payments'    


    def submit_button(self):
        """This function will change the state of the payment"""
        for record in self:
            if (record.amount == 0.00):
                raise UserError(_("Please Add The Amount Paid"))
            if record.amount - record.total_estimated_for_leagues != 0.00 and (record.amount == 0.00):
                raise UserError(_("Please Add The Amount Paid"))
            for payment in record.member_ids:
                if payment.id_payment > 0.00:
                    payment.paid_for_id = True
                    payment.member_id.write({
                        'payed_for_id': True
                    }) 

                if (payment.amount_paid > payment.fee_amount) and (payment.amount_paid > 0.00) and (payment.paid == False) and (payment.fee_amount != 0.00):
                    net_paid = payment.amount_paid + payment.traced_member_payment
                    unpaid_month = int(net_paid / payment.fee_amount)
                    remaining = net_paid % payment.fee_amount
                    i = unpaid_month
                    all_payment = self.env['each.member.payment'].search([('member_id', '=', payment.member_id.id), ('year', '=', payment.year.id)])
                    all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id), ('is_active', '=', True)])
                    new_list = []
                    for month in all_months:
                        if month.id not in all_payment.mapped('month').ids:
                            new_list.append(month.id)

                    if unpaid_month > 1:
                        for month in new_list[:unpaid_month - 1]:
                            new_payment = self.env['each.member.payment'].sudo().create({
                                'member_id': payment.member_id.id,
                                'main_office_id': payment.main_office_id.id,
                                'cell_id': payment.cell_id.id,
                                'fee_amount': payment.fee_amount,
                                'amount_remaining': 0.00,
                                'amount_paid': 0.00,
                                'state': 'paid',
                                'annual_fee': payment.annual_fee,
                                'traced_member_payment': remaining,
                                'year': payment.year.id,
                                'month': month,
                                'type_of_payment': payment.type_of_payment,
                                'subcity_id': payment.subcity_id.id,
                                'wereda_id': payment.wereda_id.id,
                                'user_id': payment.user_id.id,
                                'id_payment': 0.00,
                                'paid': True
                            })
                    payment.traced_member_payment = remaining
                    payment.member_id.track_member_fee = remaining

                if (payment.amount_paid < payment.fee_amount) and (payment.paid == False):
                    trace = payment.amount_paid - payment.fee_amount
                    payment.original = payment.traced_member_payment
                    payment.traced_member_payment += trace
                    payment.member_id.track_member_fee = payment.traced_member_payment                   

            for payment in record.league_ids:
                if payment.id_payment > 0.00:
                    payment.paid_for_id = True
                    payment.league_id.write({
                        'payed_for_id': True
                    }) 

                if (payment.amount_paid > payment.fee_amount) and (payment.amount_paid > 0.00) and (payment.paid == False) and (payment.fee_amount != 0.00):
                    net_paid = payment.amount_paid + payment.traced_league_payment
                    unpaid_month = int(net_paid / payment.fee_amount)
                    remaining = net_paid % payment.fee_amount
                    i = unpaid_month
                    all_payment = self.env['each.league.payment'].search([('league_id', '=', payment.league_id.id), ('year', '=', payment.year.id)])
                    all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id), ('is_active', '=', True)])
                    new_list = []
                    for month in all_months:
                        if month.id not in all_payment.mapped('month').ids:
                            new_list.append(month.id)

                    if unpaid_month > 1:
                        for month in new_list[:unpaid_month - 1]:
                            new_payment = self.env['each.league.payment'].sudo().create({
                                'league_id': payment.league_id.id,
                                'main_office_id': payment.main_office_id.id,
                                'cell_id': payment.cell_id.id,
                                'fee_amount': payment.fee_amount,
                                'amount_remaining': 0.00,
                                'amount_paid': 0.00,
                                'state': 'paid',
                                'annual_league_fee': payment.annual_league_fee,
                                'traced_league_payment': remaining,
                                'year': payment.year.id,
                                'month': month,
                                'type_of_payment': payment.type_of_payment,
                                'subcity_id': payment.subcity_id.id,
                                'wereda_id': payment.wereda_id.id,
                                'user_id': payment.user_id.id,
                                'id_payment': 0.00,
                                'paid': True
                            })
                    payment.traced_league_payment = remaining
                    payment.league_id.track_league_fee = remaining

                if (payment.amount_paid < payment.fee_amount) and (payment.paid == False):
                    trace = payment.amount_paid - payment.fee_amount
                    payment.original = payment.traced_league_payment
                    payment.traced_league_payment += trace
                    payment.league_id.track_league_fee = payment.traced_league_payment 
            record.state = 'submit'


    def draft_button(self):
        """This function will revert the state of payment to draft"""
        for record in self:
            record.estimated_amount_remaining = 0.00
            record.amount = 0.00
            for payment in record.member_ids:
                    payment.traced_member_payment = payment.original
                    payment.member_id.track_member_fee = payment.original
            #     if (payment.amount_paid == payment.annual_fee) and (payment.amount_paid > 0.00):
            #         all_payment = self.env['each.member.payment'].search([('member_id', '=', payment.member_id.id), ('year', '=', payment.year.id)])
            #         all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id)])
            #         for month in all_months:
            #             if month.id <= payment.month.id:
            #                 past_payment = all_payment.filtered(lambda rec: rec.month.id == month.id)
            #                 past_payment.write({
            #                     'state': 'not payed'
            #                 })
            #             else:
            #                 generated = all_payment.filtered(lambda rec: rec.month.id == month.id)
            #                 generated.unlink()
            #                 all_payment = self.env['each.member.payment'].search([('member_id', '=', payment.member_id.id), ('year', '=', payment.year.id)])
            # for payment in record.league_ids:
            #     if (payment.annual_league_fee > payment.amount_paid):
            #         payment.traced_league_payment = payment.original
            #         payment.league_id.track_league_fee = payment.original
            #     if (payment.amount_paid == payment.annual_league_fee) and (payment.amount_paid > 0.00):
            #         all_payment = self.env['each.league.payment'].search([('league_id', '=', payment.league_id.id), ('year', '=', payment.year.id)])
            #         all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id)])
            #         for month in all_months:
            #             if month.id <= payment.month.id:
            #                 past_payment = all_payment.filtered(lambda rec: rec.month.id == month.id)
            #                 past_payment.write({
            #                     'state': 'not payed'
            #                 })
            #             else:
            #                 generated = all_payment.filtered(lambda rec: rec.month.id == month.id)
            #                 generated.unlink()
            #                 all_payment = self.env['each.league.payment'].search([('league_id', '=', payment.league_id.id), ('year', '=', payment.year.id)])
            record.state = 'draft'


class Payment(models.Model):
    _inherit="membership.payment"


    # wereda_payment = fields.Many2one('sub.payment')
            