from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AppointmentStack(models.Model):
    _name='lawsuit.appointment_stack'
    _description='law suit appointments history handler'
    _rec_name = "display_name"
    _parent_name = "law_suit_id"

    
    law_suit_id = fields.Many2one('hr.lawsuit', 'Law Suit', help="field of related law suit", default=lambda self: self._context['parent_obj'], readonly="True", ondelete='cascade')
    hearing_date = fields.Date(string="Hearing Date",help="Up comming hearing date")
    court_name = fields.Char(required=True, string='Court Name')
    judge = fields.Char(required=True, string='Judge', help='Name of the Judge')
    lawyer = fields.Many2one('res.partner', string='Lawyer', help='Choose the contact of Layer from the contact list')
    ref_no = fields.Char(string="Reference Number", required=True)
    requested_date = fields.Date(string='Date')
    details = fields.Html(string='Case Details', copy=False, track_visibility='always',
                               help='More details of the case')
    
    display_name = fields.Char(store=False, default=lambda self: self.ref_no)

    @api.constrains('law_suit_id')
    def _check_state(self):
        for record in self:
            if record.law_suit_id.state in ['won', 'draft','cancel' ,'fail']:
                raise ValidationError("This Case is %s you can`t apoint." % record.law_suit_id.state)

    