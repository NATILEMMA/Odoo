# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Users(models.Model):
    _inherit = "res.users"


    @api.model
    def create(self, vals):
        """This function will create users with EAT time zone by default"""
        res = super(Users, self).create(vals)
        res.tz = 'Africa/Addis_Ababa'
        return res