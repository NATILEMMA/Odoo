# -*- coding: utf-8 -*-
# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class LibreUpdateWizard(models.TransientModel):
    _name = "libre.update.wizard"

    issue_date = fields.Datetime(string="Inspection Date", required=True, store=True)
    inspect_date = fields.Datetime(string="last Inspection Date", required=True, store=True)
    notify_date = fields.Datetime(string="Notify Date", readonly=True, store=True)
    sticker_number = fields.Char(string="Annual Sticker Number")
    approver = fields.Many2one('res.partner', string="Autoresize Body")
    user_id = fields.Many2one('res.users', string="User")

    def update_info(self):
        libre_ids = self.env.context.get('active_ids', [])
        libre_ids = libre_ids[0]
        libre = self.env['vehicle.libre'].browse(libre_ids)
        libre.write({
            'history': [(0, 0, {
                'issue_date': libre.issue_date,
                'sticker_number': libre.sticker_number,
                'approver': libre.approver.id,
                'user_id': libre.user_id.id
            })],
            'issue_date': self.issue_date,
            'sticker_number': self.sticker_number,
            'approver': self.approver.id,
            'user_id': self.user_id.id
        })

        return
