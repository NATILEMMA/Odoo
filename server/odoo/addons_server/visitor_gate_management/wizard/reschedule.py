"""This file will deal with the archiving members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
import base64
import pytz
from odoo.addons.s2u_online_appointment.helpers import functions
all_days = {
            '0': 'Monday',
            '1': 'Tuesday',
            '2': 'Wednesday',
            '3': 'Thursday',
            '4': 'Friday',
            '5': 'Saturday',
            '6': 'Sunday'
            }

class VisitorIDWidget(models.TransientModel):
    _name = "visitor.id.widget"
    _description = "This will create widgets for the visitors"

    visit = fields.Many2one('fo.visit')
    visitor_id = fields.Many2one('res.partner', string="Visitor")
    visitor_id_number = fields.Many2one('visitor.number', string="Visitor ID", domain="[('occupied', '=', False)]")


    def action_done(self):
        """This function will add ID to each visitor"""
        wizard = self.env['visitor.id.widget'].search([('id', '=', self.id)])
        if self.visitor_id and self.visitor_id_number:
            self.visitor_id.visitor_id_number = self.visitor_id_number
            self.visitor_id_number.occupied = True
            for visitor in wizard.visit.visitor:
                if not visitor.visitor_id_number:
                    wizard = self.env['visitor.id.widget'].create({
                        'visit': wizard.visit.id,
                        'visitor_id': visitor.id
                    })
                    return {
                        'name': _('Add Visitor ID'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'visitor.id.widget',
                        'view_mode': 'form',
                        'res_id': wizard.id,
                        'target': 'new'
                    }
            wizard.visit.state = 'check_in'
        else:
            raise UserError(_("Please Fill In All The Given Fields"))
        


class RescheduleVisits(models.TransientModel):
    _name = "reschedule.visit"
    _description="This model will handle the archiving members"

    date = fields.Date(string="Date", default=date.today())
    check_in_float = fields.Float(string="Check In Time")
    duration_in_float = fields.Float(string="Estimated Duration of Meeting")
    check_out_float = fields.Float(string="Check Out Time", readonly=True, store=True)
    visits_id = fields.Many2one('fo.visit')


    def ld_to_utc(self, ld):

        date_parsed = datetime.strptime(ld, "%Y-%m-%d  %H:%M")
        ethTZ = pytz.timezone("Africa/Addis_Ababa")
        local = ethTZ
        local_dt = local.localize(date_parsed, is_dst=None)
        return local_dt.astimezone(pytz.utc)