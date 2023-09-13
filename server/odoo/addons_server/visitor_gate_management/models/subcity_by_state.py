# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class StateSubCity(models.Model):
    _name = 'res.state.subcity'
    _description = "Subcities"


    state_id = fields.Many2one('res.country.state', string='Region/City Administration', required=True)
    name = fields.Char(string='Subcity Name', required=True, translate=True, size=16)
    code = fields.Char(string='Subcity Code', required=True)

    _sql_constraints = [
        ('sub_code_uniq', 'unique(state_id, code)', 'The code of the subcity must be unique by Region/City Administration !')
    ]


