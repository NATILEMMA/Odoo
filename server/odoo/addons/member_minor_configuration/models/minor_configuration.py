"""This file will deal with the modification to be made on the members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class AgeRange(models.Model):
    _name = "age.range"
    _description = "This model will handle the configuration of ages at different stages"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    for_which_stage = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('member', 'Member'), ('young_league', 'Youngster League'), ('woman_league', 'Woman League'), ('leader', 'Leader')], required=True)
    minimum_age_allowed = fields.Integer(required=True, track_visibility='onchange')
    maximum_age_allowed = fields.Integer(required=True, track_visibility='onchange')


    _sql_constraints = [
                            ('check_maximum_and_minimum', 'CHECK (maximum_age_allowed > minimum_age_allowed)', 'Maximum Age Should Be Greater Than Minimum Age')
                        ]

    @api.onchange('for_which_stage')
    def _check_duplication(self):
        """This will check if the selected has been previously selected"""
        for record in self:
            exist = self.env['age.range'].search([('for_which_stage', '=', record.for_which_stage)])
            if exist:
                raise UserError(_("Configuration for %s already Exists") % (record.for_which_stage))


class LeagueOrganization(models.Model):
    _name = "membership.organization"
    _description = "This will handle member's Organization"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Membership Organization"))

    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Membership Organization can't be Deleted. If necessary Archive."))
            return super(LeagueOrganization, self).unlink()


class LeagueResponsibility(models.Model):
    _name="league.responsibility"
    _description="This will handle leagues's responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in League Responsibility"))


    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("League Responsibility can't be Deleted. If necessary Archive."))
            return super(LeagueResponsibility, self).unlink()


class MemberResponsibility(models.Model):
    _name="members.responsibility"
    _description="This will handle member's responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Member Responsibilty"))


    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Member Responsibility can't be Deleted. If necessary Archive."))
            return super(MemberResponsibility, self).unlink()

class LeaderResponsibility(models.Model):
    _name="leaders.responsibility"
    _description="This will handle leader's responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Leader Responsibility"))

    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Leader Responsibility can't be Deleted. If necessary Archive."))
            return super(LeaderResponsibility, self).unlink()

class LeaderSubResponsibility(models.Model):
    _name="leaders.sub.responsibility"
    _description="This will handle leader's Sub-responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange', size=64)
    # leaders_responsibility = fields.Many2many('leaders.responsibility', string="Leader's Responsibility", required=True)
    total_in_woreda = fields.Integer(required=True, string="Total in Woreda")
    total_in_subcity = fields.Integer(required=True, string="Total in Subcity")
    total_in_city = fields.Integer(required=True, string="Total in City")
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE (name)', "Each Leader Sub Responsibility should be Unique"),
        ('check_on_color', 'UNIQUE (color)', "Each Color Number should be Unique"),
    ]


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Leader Sub Responsibility"))

    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Leader Sub Responsibility can't be Deleted. If necessary Archive."))
            return super(LeaderSubResponsibility, self).unlink()


class MemberSubResponsibility(models.Model):
    _name="member.sub.responsibility"
    _description="This will handle Member's Sub-responsibilities"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(translate=True, required=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Member Sub Responsibility"))

    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Member Sub Responsibility can't be Deleted. If necessary Archive."))
            return super(MemberSubResponsibility, self).unlink()


class EducationLevel(models.Model):
    _name="res.edlevel"
    _description="This model will contain education levels"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, translate=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Education Level can't be Deleted. If necessary Archive."))
            return super(EducationLevel, self).unlink()

class FieldofStudy(models.Model):
    _name="field.study"
    _description="This will craete a static fields of study"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, translate=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Field of Study"))


    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Field of Study can't be Deleted. If necessary Archive."))
            return super(FieldofStudy, self).unlink()

class UserInput(models.Model):
    _name="user.input"
    _description="This will create user inputs"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    model = fields.Char(required=True)
    user_input = fields.Char(required=True)


class InterpersonalSkills(models.Model):
    _name="interpersonal.skills"
    _description="This model will create models that will contain a list of skills and weaknesses"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, translate=True, track_visibility='onchange', size=64)
    positive = fields.Boolean(track_visibility='onchange')
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Inter Personal Skills"))

    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Interpersonal Skills can't be Deleted. If necessary Archive."))
            return super(InterpersonalSkills, self).unlink()

class EthnicGroups(models.Model):
    _name="ethnic.groups"
    _description="This model will create different ethinic groups"

    name = fields.Char(required=True, translate=True, track_visibility='onchange', size=64)
    active = fields.Boolean(default=True)


    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Ethnic Group"))


    def unlink(self):
        """This function will delete member organization"""
        for record in self:
            raise UserError(_("Ethnic Groups can't be Deleted. If necessary Archive."))
            return super(EthnicGroups, self).unlink()


class LeaderEvaluation(models.Model):
    _name="leader.evaluation"
    _description="This will handle the evaluation of leaders"

    partner_id = fields.Many2one('res.partner')
    evaluation_main_points = fields.Char(translate=True)
    key_strength = fields.Many2many('interpersonal.skills', 'positive_skill_evaluation_rel', domain="[('positive', '=', True)]")
    key_weakness = fields.Many2many('interpersonal.skills', domain="[('positive', '=', False)]")
    grade = fields.Selection(selection=[('very high', 'Very High'), ('high', 'High'), ('mid', 'Mid'), ('low', 'Low'), ('very low', 'Very Low')], default='low')
    decision = fields.Char(translate=True)
    evaluated = fields.Boolean(default=False)

    def finish_evaluation(self):
        """This will make a leader evaluated and give him a badge"""
        for record in self:
            record.evaluated = True

    def add_attachment(self):
        """This function will add attachments"""
        for record in self:
            wizard = self.env['attachment.wizard'].create({
                'res_id': record.partner_id.id,
                'res_model': 'res.partner'
            })
            return {
                'name': _('Create Attachment Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'attachment.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }



class AttachmentTypes(models.Model):
    _name="attachment.type"
    _description="This will handle the different types of attachments the member is allowed to attach"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(required=True, string="Attachment Type", translate=True, track_visibility='onchange', size=64)



    @api.onchange('name')
    def _validate_name(self):
        """This function will validate the name given"""
        for record in self:
            no = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            if record.name:
                for st in record.name:
                    if st.isdigit():
                        raise UserError(_("You Can't Have A Digit in Attachment Type"))


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    attachment_type = fields.Many2one('attachment.type')
