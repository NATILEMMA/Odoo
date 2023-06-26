"""This file will deal with the handling of donors"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class Donors(models.Model):
    _name="donors"
    _description="This model will handle Donors members"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    type_of_supporter = fields.Selection(selection=[('individual', 'Individual'), ('company', 'Company')], default='individual')
    is_company = fields.Boolean(default=False)
    name = fields.Char(translate=True, track_visibility='onchange')
    date = fields.Date(string="Date of Birth")
    age = fields.Integer(copy=False, readonly=True, store=True)
    ethnic_group = fields.Many2one('ethnic.groups')
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')])
    address = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    education_level = fields.Many2one('res.edlevel')
    field_of_study_id = fields.Many2one('field.study')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False)
    work_place = fields.Char(translate=True, copy=False, track_visibility='onchange')
    position = fields.Char(translate=True, copy=False, track_visibility='onchange')
    archive_ids = fields.One2many('archived.information', 'donor_id')
    start_of_support = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Supporter Start Year')
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', track_visibility='onchange')   
    email = fields.Char()
    website = fields.Char()
    active = fields.Boolean(default=True, track_visibility='onchange')
    reason = fields.Text(translate=True)
    saved = fields.Boolean(default=False)
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True)


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        exists = self.env['donors'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone']), ('date', '=', vals['date'])])
        if exists:
            raise UserError(_("A Donor with the same Name, Gender, Phone and Date of Birth already exists, Please make sure it isn't a duplicated data"))
        res = super(Donors, self).create(vals)
        res.saved = True
        return res


    @api.onchange('type_of_supporter')
    def _make_company(self):
        """This function will reject candate creation"""
        for record in self:
            if record.type_of_supporter == "company":
                record.age = False
                record.ethnic_group = False
                record.gender = False
                record.phone = False
                record.education_level = False
                record.field_of_study_id = False
                record.work_place = False
                record.position = False
                record.is_company = True
                record.date = False
            else:
                record.email = False
                record.website = False
                record.is_company = False

    @api.onchange('age')
    def _all_must_be_more_than_15(self):
        """This function will check if the age of the supporter is above 15"""
        for record in self:
            if record.age:
                if record.age == 0:
                    raise UserError(_("Please Add The Appropriate Age Of The Donor"))
                if record.age < 15:
                    raise UserError(_("The Donor's Age Must Be Above 15"))


    @api.onchange('date')
    def _chnage_age(self):
        """This function will change the age of person based on date"""
        for record in self:
            if record.date:
                today = date.today()
                if record.date >= today:
                    raise UserError(_("You Have To Pick A Date Before Today."))
                if today.month < record.date.month:
                    record.age = (today.year - record.date.year) - 1
                else:
                    if today.month == record.date.month and today.day < record.date.day:
                        record.age = (today.year - record.date.year) - 1
                    else:
                        record.age = today.year - record.date.year


    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 101:
                    record.is_user_input = False
                else:
                    record.is_user_input = True

    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.donor.wizard'].create({
            'donor_id': self.id
        })
        return {
            'name': _('Why Do You Want To Archive This Record?'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.donor.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            record.active = True
            all_archived = self.env['archived.information'].search([('donor_id', '=', record.id)])
            for archive in all_archived:
                if archive.archived:
                    archive.archived = False
                    archive.date_to = date.today()