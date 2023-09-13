"""This file will deal with the handling of donors"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class Donors(models.Model):
    _name="donors"
    _description="This model will handle Donors members"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_years(self):
        """This function will get the default years"""
        years = []
        eth_years = (datetime.now().year - 7)
        for num in range(eth_years, 1979, -1):
            years.append((str(num), num))
        return years


    image_1920 = fields.Binary("Image", store=True)
    type_of_supporter = fields.Selection(selection=[('individual', 'Individual'), ('company', 'Company')], default='individual')
    is_company = fields.Boolean(default=False)
    name = fields.Char(translate=True, track_visibility='onchange', size=128)
    date = fields.Date(string="Date of Birth")
    age = fields.Integer(store=True, compute="_chnage_age")
    ethnic_group = fields.Many2one('ethnic.groups')
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')])
    address = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    education_level = fields.Many2one('res.edlevel')
    field_of_study_id = fields.Many2one('field.study')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False, size=64)
    work_place = fields.Char(translate=True, copy=False, track_visibility='onchange', size=64)
    position = fields.Char(translate=True, copy=False, track_visibility='onchange', size=64)
    archive_ids = fields.One2many('archived.information', 'donor_id')
    start_of_support = fields.Selection(selection=_default_years, string='Supporter Start Year')
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', track_visibility='onchange')   
    email = fields.Char()
    website = fields.Char()
    active = fields.Boolean(default=True, track_visibility='onchange')
    reason = fields.Text(translate=True)
    saved = fields.Boolean(default=False)
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True, size=64)
    year_of_payment = fields.Many2one("fiscal.year", string='Year', store=True)
    donation_ids = fields.One2many('donation.payment', 'donor_ids', domain="[('year', '=', year_of_payment)]")

    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        phone_exists = self.env['donors'].search([('phone', '=', vals['phone'])])
        if phone_exists:
            raise UserError(_("A Donor with the same phone already exists, Please make sure it isn't a duplicated information"))
        exists = self.env['donors'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone']), ('date', '=', vals['date'])])
        if exists:
            raise UserError(_("A Donor with the same Name, Gender, Phone and Date of Birth already exists, Please make sure it isn't a duplicated data"))
        res = super(Donors, self).create(vals)
        res.saved = True
        if (res.date == False or res.age == 0) and res.type_of_supporter == 'individual':
            raise UserError(_("You Have To Pick A Date to set Age of the Donor"))
        return res


    def unlink(self):
        """This function will reject deletion of Donors"""
        for record in self:
            raise UserError(_("Donors Can Only Be Archived, Not Deleted"))
        return super(Donors, self).unlink()

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'age' in fields:
            fields.remove('age')
        return super(Donors, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.onchange('name', 'user_input', 'position')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name and record.type_of_supporter == 'individual':
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Name"))

            if record.user_input:
                for st in record.user_input:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in User Input"))

            if record.position:
                for st in record.position:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Job Position"))

    @api.onchange('email')
    def _validate_email_address(self):
        """This function will validate the email given"""
        for record in self:
            no = ['@', '.']
            if record.email:
                if '@' not in record.email or '.' not in record.email:
                    raise UserError(_("A Valid Email Address has '@' and '.'"))


    @api.onchange('website')
    def _validate_website(self):
        """This function will validate the email given"""
        for record in self:
            if record.website:
                if record.website[:4] != 'www.':
                    raise UserError(_("A Website Starts with 'www'"))
                if '.' not in record.website:
                    raise UserError(_("A Valid Website has '.'"))


    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                phone_exists = self.env['donors'].search([('phone', '=', record.phone)])
                if phone_exists:
                    raise UserError(_("A Donor with the same phone already exists, Please make sure it isn't a duplicated information"))
                for st in record.phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))

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


    @api.depends('date')
    def _chnage_age(self):
        """This function will change the age of person based on date"""
        for record in self:
            if record.date:
                today = date.today()
                if record.date >= today:
                    raise UserError(_("You Have To Pick A Date Before Today."))
                if today.month < record.date.month:
                    record.age = (today.year - record.date.year) - 1
                    if record.age == 0:
                        raise UserError(_("Please Add The Appropriate Age for The Donor"))
                    if record.age < 15:
                        raise UserError(_("The Donor's Age Must Be Above 15"))
                else:
                    if today.month == record.date.month and today.day < record.date.day:
                        record.age = (today.year - record.date.year) - 1
                        if record.age == 0:
                            raise UserError(_("Please Add The Appropriate Age for The Donor"))
                        if record.age < 15:
                            raise UserError(_("The Donor's Age Must Be Above 15"))
                    else:
                        record.age = today.year - record.date.year
                        if record.age == 0:
                            raise UserError(_("Please Add The Appropriate Age for The Donor"))
                        if record.age < 15:
                            raise UserError(_("The Donor's Age Must Be Above 15"))


    @api.onchange('year_of_payment')
    def _generate_payments(self):
        """This function will generate the payment of previous years"""
        for record in self:
            record.donation_ids = [(5, 0, 0)]
            all_donation = self.env['donation.payment'].search([('donor_ids', '=', record._origin.id), ('year', '=', record.year_of_payment.id)])
            if len(all_donation.ids) > 0:
                record.write({
                    'donation_ids': [(6, 0, all_donation.ids)]
                })

    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 34:
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