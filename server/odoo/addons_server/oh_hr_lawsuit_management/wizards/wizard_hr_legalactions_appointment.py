# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, fields, models,api


class WizardAppointment(models.TransientModel):

    _name = "wizard.appointment"
    _description = "law suit appointments"

    law_suit_id = fields.Many2one(comodel_name='hr.lawsuit', string='Law Suit', help="field of related law suit", default=lambda self: self._context['parent_obj'], readonly="True")
    hearing_date = fields.Date(string="Hearing Date",help="Up comming hearing date")
    court_name = fields.Char(required=True, string='Court Name')
    judge = fields.Char(required=True, string='Judge', help='Name of the Judge')
    lawyer = fields.Many2one(comodel_name='res.partner', string='Lawyer', help='Choose the contact of Layer from the contact list')
    ref_no = fields.Char(string="Reference Number")
    requested_date = fields.Date(string='Date')

    details = fields.Html(string='Case Details', copy=False, track_visibility='always',
                               help='More details of the case')

    def _create_appointment_value(self):
        return {
            "law_suit_id": self.law_suit_id.id,
            "hearing_date": self.hearing_date,
            "court_name": self.court_name,
            "judge":self.judge,
            "lawyer":self.lawyer.id,
            "ref_no":self.ref_no,
            "requested_date":self.requested_date,
            "details":self.details
        }

    def create_legal_appointment(self):
        appointment = self.env["lawsuit.appointment_stack"]
        appointment = self.env["lawsuit.appointment_stack"].create(
                    self._create_appointment_value()
                )
        return appointment
