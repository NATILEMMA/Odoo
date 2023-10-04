"""This file will deal with the modification to be made on the members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date



class ArchivedInformation(models.Model):
    _name = "archived.information"
    _description = "This will handle archiving_information"


    donor_id = fields.Many2one('donors')
    supporter_id = fields.Many2one('supporter.members')
    candidate_id = fields.Many2one('candidate.members')
    member_id = fields.Many2one('res.partner')
    demote_to_for_leader = fields.Selection(selection=[('member', 'Member'), ('candidate', 'Candidate'), ('supporter', 'Supporter')], default='member')
    demote_to_for_member = fields.Selection(selection=[('candidate', 'Candidate'), ('supporter', 'Supporter')], default='candidate')
    date_from = fields.Date()
    date_to = fields.Date()
    departure_reason = fields.Selection(selection=[('fired', 'Fired'), ('demote', 'Demote'), ('resigned', 'Resigned'), ('retired', 'Retired'), ('death', 'Death')], default='fired')
    additional_information = fields.Text(translate=True)
    archived = fields.Boolean(default=False)



class WorkExperience(models.Model):
    _name="work.experience"
    _description="This model will create model that will hold history of work experince"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Job Title", translate=True, size=64)
    place_of_work = fields.Char(string="Company Name", translate=True, size=64)
    years_of_service = fields.Char(translate=True, size=64)
    current_job = fields.Boolean(default=False)
    partner_id = fields.Many2one('res.partner', readonly=True)
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    import_id = fields.Many2one('importation.module')

    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Job Title"))


class Education(models.Model):
    _name = "education.history"
    _description = "This will create educational history"

    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    partner_id = fields.Many2one('res.partner')
    candidate_id = fields.Many2one('candidate.members')
    supporter_id = fields.Many2one('supporter.members')
    import_id = fields.Many2one('importation.module')