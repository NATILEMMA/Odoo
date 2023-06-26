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
    name = fields.Char(required=True, translate=True, track_visibility='onchange', store=True)
    age = fields.Integer(readonly=True, store=True)
    date = fields.Date(index=True, store=True, required=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True, store=True)
    ethnic_group = fields.Many2one('ethnic.groups', required=True, store=True)
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2one('field.study')
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region")
    region_of_birth = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Birth Place Region", store=True)
    zone_city_of_birth = fields.Char(translate=True, string="Zone/City of Birth", store=True)
    wereda_of_birth = fields.Char(translate=True, string="Woreda of Birth", store=True)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    email_address = fields.Char()
    is_user_input = fields.Boolean(default=False)
    user_input = fields.Char(translate=True)
    saved = fields.Boolean(default=False)
    kebele = fields.Char(translate=True)
    phone = fields.Char()
    email_address = fields.Char()


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        exists = self.env['register.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone']), ('date', '=', vals['date'])])
        if exists:
            raise UserError(_("A supporter with the same name, gender, phone and Date of Birth already exists, Please make sure it isn't a duplicated data"))
        return super(RegisterMembers, self).create(vals)


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


    @api.onchange('subcity_id')
    def _change_all_field_for_member(self):
        """This function will make all fields False when subcity changes"""
        for record in self:
            if record.subcity_id:
                if record.subcity_id.id != record.wereda_id.parent_id.id:
                    record.wereda_id = False


    @api.onchange('field_of_study_id')
    def _get_user_input(self):
        """This will allow user input"""
        for record in self:
            if record.field_of_study_id:
                if record.field_of_study_id.id != 101:
                    record.is_user_input = False
                else:
                    record.is_user_input = True


    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                if len(record.phone) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.phone[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))


    def create_leader(self):
        """This function will create a leader from membership"""
        for record in self:
            if record.age < 15:
                raise UserError(_("A Member Who Is Not 15 Or Above Can't Be A Leader!"))

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
                'email_address': record.email_address,
                'is_user_input': record.is_user_input,
                'user_input': record.user_input,
                'kebele': record.kebele,
                'phone': record.phone,
                'email_address': record.email_address
            })
            wizard = self.env['create.leader.wizard'].create({
                'member_id': partner.id,
                'registered_id': record.id
            })
            return {
                'name': _('Create Leader Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.leader.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }


    def create_league(self):
        """This function will create leagues from membership"""
        for record in self:
            if record.age < 15:
                raise ValidationError(_("A Person Who Is Not 15 Or Above Can't Be A League"))


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
                'email_address': record.email_address,
                'is_user_input': record.is_user_input,
                'user_input': record.user_input,
                'kebele': record.kebele,
                'phone': record.phone,
                'email_address': record.email_address
            })

            wizard = self.env['create.league.wizard'].create({
                'league_id': partner.id,
                'registered_id': record.id
            })
            return {
                'name': _('Create League Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.league.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }