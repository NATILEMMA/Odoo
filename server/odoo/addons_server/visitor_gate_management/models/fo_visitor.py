# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class VisitorIDNumber(models.Model):
    _name = "visitor.number"
    _description = "This model will create a visitor ids"

    name = fields.Char(required=True, size=64,translate=True)
    occupied = fields.Boolean(default=False, readonly=True)

    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each Visitor ID should be Unique')
                        ]

class VisitorDetails(models.Model):
    _name = 'fo.visitor'


    name = fields.Char(string="Visitor", translate=True, required=True, size=128)
    visitor_image = fields.Binary(string='Image', attachment=True)
    subcity_id = fields.Many2one('membership.handlers.parent', required=True)
    city = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", required=True)
    country_id = fields.Many2one('res.country', string='Country', readonly=True)
    phone = fields.Char(string="Phone", required=True)
    email = fields.Char(string="Email", size=64)
    id_proof = fields.Many2one('id.proof', string="ID Proof")
    id_proof_no = fields.Char(string="ID Number", help='Id proof number', translate=True, size=64)
    company_info = fields.Many2one('res.partner', string="Company", help='Visiting persons company details', domain="[('is_company', '=', True)]")


class Partner(models.Model):
    _inherit = 'res.partner'
    _description = 'visitor profile detail information'

    def _default_country(self):
        return self.env['res.country'].search([('id', '=', 69)], limit=1).id


    city_id = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region/City Administrations")
    subcity = fields.Many2one('res.state.subcity', domain="[('state_id', '=', city_id)]")
    country_id = fields.Many2one('res.country', string='Country', default=_default_country, readonly=True)
    woreda_id = fields.Char(translate=True)
    id_proof = fields.Many2one('id.proof', string="ID Proof")
    id_proof_no = fields.Char(string="ID Number", help='Id proof number', translate=True, size=64)
    company_info = fields.Many2one('res.partner', string="Company", help='Visiting persons company details', domain="[('is_company', '=', True)]")
    visit_count = fields.Integer(string='# Visits', compute="compute_visit_count", store=True)
    visitor_id_number = fields.Many2one('visitor.number', string="Visitor ID Number")

    _sql_constraints = [
        ('field_uniq_email_and_id_proof', 'unique (id_proof_no,phone)', "Please make sure ID Proof and Phone is unique !"),
    ]

    # @api.model
    # def create(self, vals):
    #     """This function will create visitor"""
    #     exists = self.env['fo.visitor'].search([('phone', '=', vals['phone'])])
    #     if exists:
    #         raise UserError(_("A Visitor With This Phone Number Already Exists. Please Make Sure You Wrote Down The Correct Phone Number"))
    #     return super(VisitorDetails, self).create(vals)


    def unlink(self):
        """This function will delete a visitor"""
        for record in self:
            if record.visitor_id_number:
                raise UserError(_("You Can't Delete A Visitor Whose Visitor ID Hasn't Been Returned"))
        return super(Partner, self).unlink()

    def compute_visit_count(self):
        for record in self:
            data = self.env['fo.visit'].search([('visitor', 'in', [record.id]), ('visiting_employee.user_id', 'in', [self.env.user.id])])
            if data:
                record.visit_count = len(data.ids)
            else:
                record.visit_count = 0
    

    # @api.onchange('name')
    # def _validate_name(self):
    #     """This function will validate the name given"""
    #     for record in self:
    #         no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    #         if record.name:
    #             for st in record.name:
    #                 if st.isdigit():
    #                     raise UserError(_("You Can't Have A Digit in Name"))

    # @api.onchange('email')
    # def _validate_email_address(self):
    #     """This function will validate the email given"""
    #     for record in self:
    #         no = ['@', '.']
    #         if record.email:
    #             if '@' not in record.email or '.' not in record.email:
    #                 raise UserError(_("A Valid Email Address has '@' and '.'"))


    # @api.onchange('phone')
    # def _proper_phone_number(self):
    #     """This function will check if phone is of proper format"""
    #     for record in self:
    #         if record.phone:
    #             exists = self.env['fo.visitor'].search([('phone', '=', record.phone)])
    #             if exists:
    #                 raise UserError(_("A Visitor With This Phone Number Already Exists. Please Make Sure You Wrote Down The Correct Phone Number"))
    #             for st in record.phone:
    #                 if not st.isdigit():
    #                     raise UserError(_("You Can't Have Characters in a Phone Number"))
    #             if record.phone[0] != '0':
    #                 raise UserError(_("A Valid Phone Number Starts With 0"))
    #             if len(record.phone) != 10:
    #                 raise UserError(_("A Valid Phone Number Has 10 Digits"))


class VisitorProof(models.Model):
    _name = 'id.proof'
    _description = "This Model will handle ID proofs"

    name = fields.Char(string="Name", translate=True, required=True, size=64)

    _sql_constraints = [
                            ('Check on name', 'UNIQUE(name)', 'Each ID Proof should be Unique')
                        ]


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in ID Proof"))









