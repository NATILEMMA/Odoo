# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
##############################################################################

from odoo import models, fields, api


class VisitorIDNumber(models.Model):
    _name = "visitor.number"
    _description = "This model will create a visitor ids"

    name = fields.Char(required=True)
    occupied = fields.Boolean(default=False, readonly=True)

class VisitorDetails(models.Model):
    _name = 'fo.visitor'
    _description = 'visitor profile detail information'

    def _default_country(self):
        return self.env['res.country'].search([('id', '=', 69)], limit=1).id


    name = fields.Char(string="Visitor", required=True)
    visitor_image = fields.Binary(string='Image', attachment=True)
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', default=_default_country, ondelete='restrict')
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    id_proof = fields.Many2one('id.proof', string="ID Proof")
    id_proof_no = fields.Char(string="ID Number", help='Id proof number', translate=True)
    company_info = fields.Many2one('res.partner', string="Company", help='Visiting persons company details')
    visit_count = fields.Integer(compute='_no_visit_count', string='# Visits')
    visitor_id_number = fields.Many2one('visitor.number', string="Visitor ID Number")

    _sql_constraints = [
        ('field_uniq_email_and_id_proof', 'unique (email,id_proof_no)', "Please make sure ID Proof or Email is unique !"),
    ]

    def _no_visit_count(self):
        data = self.env['fo.visit'].search([('visitor', 'in', self.ids), ('state', '!=', 'cancel')]).ids
        self.visit_count = len(data)


class VisitorProof(models.Model):
    _name = 'id.proof'
    _rec_name = 'id_proof'

    id_proof = fields.Char(string="Name", translate=True, required=True)








