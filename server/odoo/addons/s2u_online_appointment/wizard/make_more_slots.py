# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class MakeMoreSlots(models.TransientModel):
    _name = "make.more.slot"
    _description = "This model will create more slots"


    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    user_id = fields.Many2one('hr.employee', string='User')
    day = fields.Selection(selection=_get_week_days, default='0', string="Day", readonly=True)
    slot_ids = fields.Many2many('times', required=True)

    def action_done(self):
        """This function will create slots"""
        wizard = self.env['make.more.slot'].search([('id', '=', self.id)])
        self.day = wizard.day
        if self.slot_ids:
            for slot in self.slot_ids:
                self.env['s2u.appointment.slot'].sudo().create({
                    'user_id': wizard.user_id.id,
                    'day': wizard.day,
                    'slot': slot.time
                })
