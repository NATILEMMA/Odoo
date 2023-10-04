"""This file will deal with the Direct registration"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class RegisterMembers(models.Model):
    _name="register.members"
    _description="This model will create registration of members beform they become leagues or leaders"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(translate=True, track_visibility='onchange', store=True, size=128)
    first_name  = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    father_name = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    grand_father_name = fields.Char(translate=True, track_visibility='onchange', store=True, size=32, required=True)
    age = fields.Integer(readonly=True, store=True)
    date = fields.Date(index=True, store=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True, store=True)
    ethnic_group = fields.Many2one('ethnic.groups', required=True, store=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region/City Administrations")
    region_of_birth = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Birth Place Region/City Administrations", store=True)
    zone_city_of_birth = fields.Char(translate=True, string="Zone/City of Birth", store=True, size=64)
    wereda_of_birth = fields.Char(translate=True, string="Woreda of Birth", store=True, size=64)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    residential_subcity = fields.Char(string="Residential Subcity", required=True, store=True)
    residential_wereda = fields.Char(string="Residential Woreda", required=True)
    email_address = fields.Char()
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True, size=64)
    saved = fields.Boolean(default=False)
    kebele = fields.Char(translate=True, size=64)
    phone = fields.Char(required=True)
    created = fields.Date()


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        phone_exists = self.env['register.members'].search([('phone', '=', vals['phone'])])
        if phone_exists:
            raise UserError(_("A Registree with the same phone already exists, Please make sure it isn't a duplicated information"))
        exists = self.env['register.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone']), ('date', '=', vals['date'])])
        if exists:
            raise UserError(_("A Registree with the same Name, Gender, Phone and Date of Birth already exists, Please make sure it isn't a duplicated data"))
        res = super(RegisterMembers, self).create(vals)
        res.created = res.create_date.date()
        res.name = res.first_name + " " + res.father_name + " " + res.grand_father_name
        res.saved = True
        if res.date == False or res.age == 0:
            raise UserError(_("You Have To Pick A Date to set Age of the Registree"))
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'age' in fields:
            fields.remove('age')
        return super(RegisterMembers, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)


    @api.onchange('name', 'user_input')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Name"))

            if record.user_input:
                for st in record.user_input:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in User Input"))

    @api.onchange('email_address')
    def _validate_email_address(self):
        """This function will validate the email given"""
        for record in self:
            no = ['@', '.']
            if record.email_address:
                if '@' not in record.email_address or '.' not in record.email_address:
                    raise UserError(_("A Valid Email Address has '@' and '.'"))

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                phone_exists = self.env['register.members'].search([('phone', '=', record.phone)])
                if phone_exists:
                    raise UserError(_("A Registree with the same phone already exists, Please make sure it isn't a duplicated information"))
                for st in record.phone:
                    if not st.isdigit():
                        raise UserError(_("You Can't Have Characters in a Phone Number"))
                if record.phone[0] != '0':
                    raise UserError(_("A Valid Phone Number Starts With 0"))
                if len(record.phone) != 10:
                    raise UserError(_("A Valid Phone Number Has 10 Digits"))

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
                    if record.age == 0:
                        raise UserError(_("Please Add The Appropriate Age for The Registree"))
                    if record.age < 15:
                        raise UserError(_("The Registree's Age Must Be Above 15"))
                else:
                    if today.month == record.date.month and today.day < record.date.day:
                        record.age = (today.year - record.date.year) - 1
                        if record.age == 0:
                            raise UserError(_("Please Add The Appropriate Age for The Registree"))
                        if record.age < 15:
                            raise UserError(_("The Registree's Age Must Be Above 15"))
                    else:
                        record.age = today.year - record.date.year
                        if record.age == 0:
                            raise UserError(_("Please Add The Appropriate Age for The Registree"))
                        if record.age < 15:
                            raise UserError(_("The Registree's Age Must Be Above 15"))


    @api.onchange('subcity_id')
    def _change_all_field_for_member(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False


    # @api.onchange('residential_subcity_id')
    # def _change_all_residential_field_for_registred(self):
    #     """This function will make all fields False when subcity changes"""
    #     for record in self:
    #         if record.residential_subcity_id:
    #             if record.residential_subcity_id.id != record.residential_wereda_id.parent_id.id:
    #                 record.residential_wereda_id = False


    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 34:
                    record.is_user_input = False
                else:
                    record.is_user_input = True


    def create_leader(self):
        """This function will create a leader from membership"""
        for record in self:

            age_limit = self.env['age.range'].search([('for_which_stage', '=', 'leader')])
            if not age_limit:
                raise UserError(_("Please Set Age Limit for Leader in the Configuration"))
            if record.age < age_limit.minimum_age_allowed or record.age > age_limit.maximum_age_allowed:
                raise UserError(_("This Age isn't within the Age Limit Range given for Leader"))

            partner = self.env['res.partner'].create({
                'image_1920': record.image_1920,
                'name': record.name,
                'age': record.age,
                'date': record.date,
                'gender': record.gender,
                'ethnic_group': record.ethnic_group.id,
                'education_level': record.education_level.id,
                'field_of_study_id': record.field_of_study_id.id,
                'region': record.region.id,
                'region_of_birth': record.region_of_birth.id,
                'zone_city_of_birth': record.zone_city_of_birth,
                'wereda_of_birth': record.wereda_of_birth,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'residential_subcity': record.residential_subcity,
                'residential_wereda': record.residential_wereda,
                'email_address': record.email_address,
                'is_user_input': record.is_user_input,
                'user_input': record.user_input,
                'kebele': record.kebele,
                'phone': record.phone,
                'email_address': record.email_address
            })
            wizard = self.env['create.leader.wizard'].create({
                'member_id': partner.id,
                'registered_id': record.id,
                'wereda_id': record.wereda_id.id,
            })
            return {
                'name': _('Create Leader Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.leader.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }